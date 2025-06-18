# eazybank-agentverse-aws-lambda 
# [Architecture + Testing Instructions]
![image](https://github.com/user-attachments/assets/3a7b43ba-081d-42f8-b5e5-30b8e7fcffbd)

## Testing Instructions: EazyBank AgentVerse

**Access:**

*   Open your web browser and navigate to: [https://eazybank.born2learn.xyz/](https://eazybank.born2learn.xyz/)
    *   (Hosted in AWS, ap-northeast-1 region)

**Basic Interaction:**

*   **Start Conversation:** Enter a simple greeting like "Hi" to initiate the conversation.

**Account Application Status:**

*   **Initiate Inquiry:** Enter: "I have recently applied for a savings account at EazyBank. I want to know the status of my application."
*   **Mobile Number Prompt:** The agent will prompt you for your registered mobile number.
*   **Test Mobile Numbers:** Use the following test mobile numbers:
    *   2016166576
    *   2016166577
    *   2016166578
    *   2016166579
    *   2016166580
*   **Expected Results Based on Mobile Number:**
    *   **2016166576 & 2016166580:** Account application has been approved. Verify the displayed account details (account number, balance, credit card).
    *   **2016166577, 2016166578, & 2016166579:** Account application has been rejected. Verify the displayed rejection reason.

**Rejection Details:**

*   **Request More Information:** After receiving a rejection reason, ask for more details (e.g., "Why was my application rejected?", "Tell me more about the rejection reason").
*   **Verify Explanation:** Verify the detailed explanation provided is clear and understandable.

**Human Agent Handoff:**

*   **Request Handoff:** At any point, you can ask to speak to a human agent (e.g., "I want to speak to a human agent", "Connect me to a human agent", "I need help from a human").
*   **Verify Indication:** Verify that the application indicates you are being transferred to a human agent (e.g., a message like "You are being connected to a human agent shortly").

**Expected Outcomes:**

*   Smooth transitions between AI agents.
*   Accurate account application status retrieval based on the provided test mobile numbers.
*   Clear and detailed explanations for rejection reasons, going beyond the initial rejection reason.
*   Successful human agent handoff indication with a clear message to the user.

**Notes:**

*   Ensure you are using the exact mobile numbers provided for testing purposes.
*   Pay attention to the clarity and helpfulness of the agent's responses.
*   Test the human handoff from different points in the conversation to ensure it functions correctly in various scenarios.
