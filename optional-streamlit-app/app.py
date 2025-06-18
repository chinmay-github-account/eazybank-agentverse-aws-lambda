from dotenv import load_dotenv
import json
import logging
import logging.config
import os
import re
from services import bedrock_agent_runtime
import streamlit as st
import uuid
import yaml
from datetime import datetime

load_dotenv()

# Configure logging using YAML
if os.path.exists("logging.yaml"):
    with open("logging.yaml", "r") as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)
else:
    log_level = logging.getLevelNamesMapping()[(os.environ.get("LOG_LEVEL", "INFO"))]
    logging.basicConfig(level=log_level)

logger = logging.getLogger(__name__)

# Get config from environment variables
agent_id = os.environ.get("BEDROCK_AGENT_ID")
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")  # TSTALIASID is the default test alias ID
ui_title = os.environ.get("BEDROCK_AGENT_TEST_UI_TITLE", "Welcome to EazyBank Support Agent")
ui_icon = os.environ.get("BEDROCK_AGENT_TEST_UI_ICON", ":bank:")
page_icon = ui_icon

# --- Streamlit Configuration ---
st.set_page_config(
    page_title=ui_title,
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS Styling ---
st.markdown(
    """
    <style>
    body {
        font-family: 'Google Sans', sans-serif;
        background: linear-gradient(135deg, #026560, #b03b60); /* A soft, colorful gradient */
        color: #333;
    }

    .stChatMessage {
        background-color: #f3f6fc;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
    }

    .agent-icons {
        font-size: 2em;
        margin-top: 10px;
        color: #e67e22; /* A DevOps-y orange */
    }

    .agent-icons i {
        margin: 0 10px;
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    """,
    unsafe_allow_html=True,
)

# --- App Initialization ---
def init_session_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.citations = []
    st.session_state.trace = {}

if len(st.session_state.items()) == 0:
    init_session_state()

# --- Variable Definitions (MISSING BEFORE) ---
trace_types_map = {
    "Pre-Processing": ["preGuardrailTrace", "preProcessingTrace"],
    "Orchestration": ["orchestrationTrace"],
    "Post-Processing": ["postProcessingTrace", "postGuardrailTrace"]
}

trace_info_types_map = {
    "preProcessingTrace": ["modelInvocationInput", "modelInvocationOutput"],
    "orchestrationTrace": ["invocationInput", "modelInvocationInput", "modelInvocationOutput", "observation", "rationale"],
    "postProcessingTrace": ["modelInvocationInput", "modelInvocationOutput", "observation"]
}

# JSON Serializer function
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# --- Sidebar ---
with st.sidebar:
    st.title("Trace")

    # Show each trace type in separate sections
    step_num = 1
    for trace_type_header in trace_types_map:
        st.subheader(trace_type_header)

        # Organize traces by step similar to how it is shown in the Bedrock console
        has_trace = False
        for trace_type in trace_types_map[trace_type_header]:
            if trace_type in st.session_state.trace:
                has_trace = True
                trace_steps = {}

                for trace in st.session_state.trace[trace_type]:
                    # Each trace type and step may have different information for the end-to-end flow
                    if trace_type in trace_info_types_map:
                        trace_info_types = trace_info_types_map[trace_type]
                        for trace_info_type in trace_info_types:
                            if trace_info_type in trace:
                                trace_id = trace[trace_info_type]["traceId"]
                                if trace_id not in trace_steps:
                                    trace_steps[trace_id] = [trace]
                                else:
                                    trace_steps[trace_id].append(trace)
                                break
                    else:
                        trace_id = trace["traceId"]
                        trace_steps[trace_id] = [
                            {
                                trace_type: trace
                            }
                        ]

                # Show trace steps in JSON similar to the Bedrock console
                for trace_id in trace_steps.keys():
                    with st.expander(f"Trace Step {str(step_num)}", expanded=False):
                        for trace in trace_steps[trace_id]:
                            try:
                                trace_str = json.dumps(trace, indent=2, default=json_serial)  # Use json_serial
                                st.code(trace_str, language="json", line_numbers=True, wrap_lines=True)
                            except TypeError as e:
                                st.error(f"Error serializing trace: {e}")
                        step_num += 1
        if not has_trace:
            st.text("None")

    st.subheader("Citations")
    if len(st.session_state.citations) > 0:
        citation_num = 1
        for citation in st.session_state.citations:
            for retrieved_ref_num, retrieved_ref in enumerate(citation["retrievedReferences"]):
                with st.expander(f"Citation [{str(citation_num)}]", expanded=False):
                    try:
                        citation_str = json.dumps(
                            {
                                "generatedResponsePart": citation["generatedResponsePart"],
                                "retrievedReference": citation["retrievedReferences"][retrieved_ref_num]
                            },
                            indent=2,
                            default=json_serial  # Use json_serial
                        )
                        st.code(citation_str, language="json", line_numbers=True, wrap_lines=True)
                    except TypeError as e:
                        st.error(f"Error serializing citation: {e}")
                    citation_num = citation_num + 1
    else:
        st.text("None")

# --- Main App UI ---
st.markdown(
    f"""
    <div style="text-align: center;">
        <h3 style="color: DeepSkyBlue; font-size: 2.5em;">{ui_title}</h3>
        <div class="agent-icons">
            <i class="fas fa-university"></i>
            <i class="fas fa-money-bill-wave"></i>
            <i class="fas fa-comments-dollar"></i>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input that invokes the agent
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        full_response = ""  # Accumulate the response

        with st.spinner():  # Keep the spinner active during the streaming response
            response = bedrock_agent_runtime.invoke_agent(
                agent_id,
                agent_alias_id,
                st.session_state.session_id,
                prompt
            )
            output_text = response["output_text"]

            # Check if the output is a JSON object with the instruction and result fields
            try:
                output_json = json.loads(output_text, strict=False)
                if "instruction" in output_json and "result" in output_json:
                    output_text = output_json["result"]
            except json.JSONDecodeError as e:
                pass

            # Add citations
            if len(response["citations"]) > 0:
                citation_num = 1
                output_text = re.sub(r"%\[(\d+)\]%", r"<sup>[\1]</sup>", output_text)
                num_citation_chars = 0
                citation_locs = ""
                for citation in response["citations"]:
                    for retrieved_ref in citation["retrievedReferences"]:
                        citation_marker = f"[{citation_num}]"
                        citation_locs += f"\n<br>{citation_marker} {retrieved_ref['location']['s3Location']['uri']}"
                        citation_num += 1
                    output_text += f"\n{citation_locs}"

            full_response += output_text

        st.session_state.messages.append({"role": "assistant", "content": full_response})  # Use accumulated response
        st.session_state.citations = response["citations"]
        st.session_state.trace = response["trace"]
        st.markdown(full_response, unsafe_allow_html=True)  # Display accumulated response
