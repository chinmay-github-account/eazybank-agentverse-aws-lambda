import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def invoke_agent(agent_id, agent_alias_id, session_id, prompt):
    try:
        client = boto3.client(service_name="bedrock-agent-runtime")

        response = client.invoke_agent(
            agentId='JYFK4LXLKS',
            agentAliasId='GVRAPMGFG2',
            enableTrace=True,
            sessionId=session_id,
            inputText=prompt
        )

        output_text = ""
        citations = []
        trace = {}

        for event in response.get("completion"):
            # Combine the chunks to get the output text
            if "chunk" in event:
                chunk = event["chunk"]
                output_text += chunk["bytes"].decode()
                if "attribution" in chunk:
                    citations += chunk["attribution"]["citations"]

            # Extract trace information from all events
            if "trace" in event:
                for trace_type in ["guardrailTrace", "preProcessingTrace", "orchestrationTrace", "postProcessingTrace"]:
                    if trace_type in event["trace"]["trace"]:
                        mapped_trace_type = trace_type
                        if trace_type == "guardrailTrace":
                            mapped_trace_type = "preGuardrailTrace" if not trace.get("preGuardrailTrace") else "postGuardrailTrace"

                        if mapped_trace_type not in trace:
                            trace[mapped_trace_type] = []
                        trace[mapped_trace_type].append(event["trace"]["trace"][trace_type])

    except ClientError as e:
        logger.error(f"Error invoking agent: {e}") # Log the error
        raise  # Re-raise the exception

    return {
        "output_text": output_text,
        "citations": citations,
        "trace": trace
    }
