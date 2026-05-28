import os
from textwrap import dedent

import streamlit as st


APP_TITLE = "ServiceNow QA Test Case Generator"


def get_setting(name, default=""):
    if name in os.environ:
        return os.environ[name]
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


AGENT_INSTRUCTIONS = """
You are the ServiceNow QA Test Case Generator Agent.

Your purpose is to help QA analysts quickly create clear, executable test cases
for ServiceNow work items.

You accept the following inputs:
- Story title
- Description
- Acceptance criteria
- Affected module/table
- Roles involved

When the user provides a ServiceNow story, defect, or requirement, generate QA
test cases that are practical for manual testing.

Follow these rules:
1. Identify the affected ServiceNow area, such as Incident, Change, Problem,
   Request, Catalog Item, CMDB, Flow Designer, Notifications, Integrations,
   ACLs, Reports, or Portal.
2. Extract the business goal and expected user behavior.
3. Identify the roles or personas that need testing.
4. Generate test cases using this format:
   - Test Case ID
   - Title
   - Type
   - Preconditions
   - Test Data
   - Steps
   - Expected Result
   - Priority
5. Use these test case types when relevant:
   - Positive
   - Negative
   - Edge
   - Regression
   - Security
   - Integration
   - Data Validation
6. Include role-based tests when permissions or approvals are involved.
7. Include regression tests for nearby ServiceNow functionality that may be impacted.
8. Include negative tests for invalid inputs, missing mandatory fields, incorrect
   states, unauthorized users, and failed integrations where relevant.
9. Include edge cases for boundary values, duplicate records, inactive
   users/groups, cancelled workflows, reopened records, and unusual state
   transitions where relevant.
10. Keep the test cases practical for a QA analyst to execute manually.
11. If information is missing, make reasonable assumptions and list them separately.
12. Do not invent overly broad tests unrelated to the described change.
13. Use ServiceNow terminology accurately.

Return every response using this structure:

Summary:
Briefly summarize what is being tested.

Assumptions:
List any assumptions made.

Test Data Needed:
List users, roles, records, groups, catalog items, or sample data needed.

Test Cases:
Provide the test cases in a human-readable structured list, not a table.
Each test case must start on a new line with a bold heading like:
**TC-001 - Validate expected happy path behavior**
Then list Type, Priority, Preconditions, Test Data, Steps, and Expected Result
under that heading.

Regression Checks:
List related areas that should be checked.

Questions / Gaps:
List anything the user should clarify.
"""


def build_prompt(story_title, description, acceptance_criteria, affected_module, roles):
    return f"""{AGENT_INSTRUCTIONS}

Generate ServiceNow QA test cases for this work item:

Title:
{story_title}

Description:
{description}

Acceptance Criteria:
{acceptance_criteria}

Affected Module/Table:
{affected_module}

Roles Involved:
{roles}
"""


def infer_keywords(text):
    value = text.lower()
    keywords = {
        "approval": any(word in value for word in ["approval", "approve", "approver"]),
        "catalog": any(word in value for word in ["catalog", "request item", "ritm", "variable"]),
        "incident": "incident" in value,
        "change": "change" in value,
        "notification": any(word in value for word in ["notification", "email", "event"]),
        "integration": any(word in value for word in ["integration", "rest", "soap", "api", "import set"]),
        "security": any(word in value for word in ["role", "acl", "permission", "access"]),
        "flow": any(word in value for word in ["flow", "workflow", "trigger"]),
    }
    return keywords


def fallback_generator(story_title, description, acceptance_criteria, affected_module, roles):
    combined = " ".join([story_title, description, acceptance_criteria, affected_module, roles])
    keywords = infer_keywords(combined)
    module = affected_module.strip() or "the affected ServiceNow module/table"
    role_text = roles.strip() or "standard QA user and relevant fulfiller role"

    tests = [
        {
            "id": "TC-001",
            "title": "Validate expected happy path behavior",
            "type": "Positive",
            "preconditions": f"A test record exists or can be created in {module}.",
            "data": f"User with required role: {role_text}.",
            "steps": "Create or open the target record; enter valid required data; perform the requested action; save or submit the record.",
            "expected": "The record saves successfully and the behavior matches the acceptance criteria.",
            "priority": "High",
        },
        {
            "id": "TC-002",
            "title": "Validate required field and invalid input handling",
            "type": "Negative",
            "preconditions": f"User can access {module}.",
            "data": "Blank mandatory fields or invalid sample values.",
            "steps": "Attempt the workflow with missing or invalid data; submit or save the record.",
            "expected": "ServiceNow prevents the action or displays a clear validation message without corrupting record data.",
            "priority": "High",
        },
        {
            "id": "TC-003",
            "title": "Validate role-based access",
            "type": "Security",
            "preconditions": "At least one authorized and one unauthorized user are available.",
            "data": f"Authorized role/persona: {role_text}; unauthorized user without the required role.",
            "steps": "Impersonate the authorized user and perform the action; repeat with the unauthorized user.",
            "expected": "Authorized users can complete permitted actions; unauthorized users cannot access or modify restricted data.",
            "priority": "High",
        },
        {
            "id": "TC-004",
            "title": "Validate state and data integrity after update",
            "type": "Data Validation",
            "preconditions": "A target record exists before testing begins.",
            "data": "Known before-and-after field values.",
            "steps": "Perform the configured action; refresh the form; verify field values, state, activity log, and related records.",
            "expected": "Only expected fields change, related records are accurate, and the activity history reflects the action.",
            "priority": "Medium",
        },
        {
            "id": "TC-005",
            "title": "Validate nearby module regression",
            "type": "Regression",
            "preconditions": f"Existing records are available in {module}.",
            "data": "Existing record plus a newly created test record.",
            "steps": "Open, update, save, search, filter, and view related lists for affected records.",
            "expected": "Existing ServiceNow behavior continues to work and no unrelated form, list, or related-list behavior is broken.",
            "priority": "Medium",
        },
    ]

    if keywords["approval"]:
        tests.append(
            {
                "id": "TC-006",
                "title": "Validate approval routing and approval outcome",
                "type": "Positive",
                "preconditions": "An approver or approval group is configured and active.",
                "data": "Record that meets approval criteria.",
                "steps": "Submit the record; verify an approval is generated; approve the request; refresh the source record.",
                "expected": "Approval is routed correctly and the source record proceeds only after approval is granted.",
                "priority": "High",
            }
        )

    if keywords["notification"]:
        tests.append(
            {
                "id": "TC-007",
                "title": "Validate notification trigger and recipients",
                "type": "Regression",
                "preconditions": "Email sending or email log validation is available.",
                "data": "Recipient user or group with a valid email address.",
                "steps": "Perform the triggering action; check notification/email logs and recipient details.",
                "expected": "The correct notification is sent to the expected recipients with accurate content.",
                "priority": "Medium",
            }
        )

    if keywords["integration"]:
        tests.append(
            {
                "id": "TC-008",
                "title": "Validate integration success and failure handling",
                "type": "Integration",
                "preconditions": "Integration endpoint or mock response is available.",
                "data": "Valid payload and one invalid or failed response scenario.",
                "steps": "Trigger the integration with valid data; repeat with an error condition; inspect logs and record updates.",
                "expected": "Successful calls update ServiceNow correctly; failed calls are logged and handled without silent data loss.",
                "priority": "High",
            }
        )

    test_blocks = "\n\n".join(
        dedent(
            f"""
            **{test["id"]} - {test["title"]}**
            - Type: {test["type"]}
            - Priority: {test["priority"]}
            - Preconditions: {test["preconditions"]}
            - Test Data: {test["data"]}
            - Steps: {test["steps"]}
            - Expected Result: {test["expected"]}
            """
        ).strip()
        for test in tests
    )

    return "\n".join(
        [
            "## Summary",
            f"These test cases validate `{story_title or 'the requested ServiceNow change'}` for `{module}`.",
            "",
            "## Assumptions",
            "- The QA tester has access to an appropriate ServiceNow test instance.",
            "- Required users, groups, and roles can be created or impersonated.",
            "- Acceptance criteria are the primary source of expected behavior.",
            "",
            "## Test Data Needed",
            f"- Test user(s): {role_text}",
            f"- Test record(s) in {module}",
            "- Valid and invalid field values",
            "- Active assignment group, approver, or related records where applicable",
            "",
            "## Test Cases",
            "",
            test_blocks,
            "",
            "## Regression Checks",
            f"- Confirm existing create, update, save, and list behavior still works in {module}.",
            "- Verify mandatory fields, UI policies, client scripts, business rules, and related lists still behave as expected.",
            "- Confirm no unexpected notifications, approvals, or state changes occur.",
            "",
            "## Questions / Gaps",
            "- Are there specific roles, groups, or personas that must be tested?",
            "- Are there special state transitions, approvals, notifications, or integrations tied to this change?",
            "- Are there existing defects or known limitations that QA should include?",
        ]
    )


def generate_with_langchain(prompt, model_name):
    try:
        from langchain_ollama import ChatOllama
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError as exc:
        raise RuntimeError(
            "LangChain Ollama packages are not installed. Run `pip install -r requirements.txt`."
        ) from exc

    llm = ChatOllama(model=model_name, temperature=0.2)
    response = llm.invoke(
        [
            SystemMessage(content=AGENT_INSTRUCTIONS),
            HumanMessage(content=prompt),
        ]
    )
    return response.content


def generate_with_huggingface(prompt, model_name, token, provider):
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError(
            "Hugging Face package is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    if not token:
        raise RuntimeError(
            "Add a Hugging Face token in the sidebar or set the HF_TOKEN environment variable."
        )

    try:
        client = InferenceClient(provider=provider, api_key=token, timeout=90)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1800,
        )
        return response.choices[0].message.content
    except Exception as exc:
        message = str(exc)
        if "memory layout cannot be allocated" in message.lower():
            raise RuntimeError(
                "The Hugging Face provider could not allocate enough memory for this model. "
                "Try `Qwen/Qwen3-0.6B`, `HuggingFaceTB/SmolLM3-3B`, or switch to the built-in generator."
            ) from exc
        raise


HF_MODEL_OPTIONS = [
    "Qwen/Qwen3-0.6B",
    "HuggingFaceTB/SmolLM3-3B",
    "Qwen/Qwen3-4B-Instruct-2507",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
]


def get_default_hf_model():
    configured_model = get_setting("HF_MODEL", HF_MODEL_OPTIONS[0])
    if configured_model in HF_MODEL_OPTIONS:
        return configured_model
    return HF_MODEL_OPTIONS[0]


def render_app():
    st.set_page_config(page_title=APP_TITLE, page_icon="QA", layout="wide")

    st.title(APP_TITLE)
    st.caption("Generate practical manual QA test cases for ServiceNow stories, defects, and requirements.")

    with st.sidebar:
        st.header("Generation")
        mode = st.radio(
            "Engine",
            ["Hugging Face Inference API", "Built-in free generator", "LangChain + local Ollama"],
            help="Use Hugging Face for faster hosted inference, the built-in generator with no setup, or a local Ollama model.",
        )
        model_name = st.text_input("Ollama model", value=get_setting("OLLAMA_MODEL", "qwen3"))
        hf_model_choice = st.selectbox(
            "Hugging Face model",
            HF_MODEL_OPTIONS,
            index=HF_MODEL_OPTIONS.index(get_default_hf_model()),
            help="Smaller models are less likely to hit provider memory errors.",
        )
        hf_model = st.text_input(
            "Custom Hugging Face model",
            value=hf_model_choice,
            help="Use this to override the selected model.",
        )
        hf_provider = st.text_input("Hugging Face provider", value=get_setting("HF_PROVIDER", "auto"))
        hf_token = st.text_input(
            "Hugging Face token",
            value=get_setting("HF_TOKEN", ""),
            type="password",
            help="Create a token in Hugging Face settings with Inference Providers permission.",
        )
        st.divider()
        st.markdown("**Expected inputs**")
        st.markdown("- Story title\n- Description\n- Acceptance criteria\n- Affected module/table\n- Roles involved")

    with st.form("qa_agent_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            story_title = st.text_input("Story title", placeholder="Add approval for high-priority incidents")
            affected_module = st.text_input("Affected module/table", placeholder="Incident / incident")
            roles = st.text_input("Roles involved", placeholder="ITIL user, assignment group manager, admin")

        with col_b:
            description = st.text_area(
                "Description",
                height=130,
                placeholder="Describe the ServiceNow change, defect, or requirement.",
            )
            acceptance_criteria = st.text_area(
                "Acceptance criteria",
                height=130,
                placeholder="- Approval is required for P1/P2 incidents\n- P3-P5 should not require approval",
            )

        submitted = st.form_submit_button("Generate test cases", type="primary")

    if submitted:
        if not any([story_title, description, acceptance_criteria, affected_module, roles]):
            st.warning("Add at least one input so the agent has something to work with.")
            return

        prompt = build_prompt(story_title, description, acceptance_criteria, affected_module, roles)

        with st.spinner("Generating ServiceNow QA test cases..."):
            try:
                if mode == "Hugging Face Inference API":
                    output = generate_with_huggingface(prompt, hf_model, hf_token, hf_provider)
                elif mode == "LangChain + local Ollama":
                    output = generate_with_langchain(prompt, model_name)
                else:
                    output = fallback_generator(
                        story_title,
                        description,
                        acceptance_criteria,
                        affected_module,
                        roles,
                    )
            except Exception as exc:
                st.error(str(exc))
                st.info("Falling back to the built-in free generator.")
                output = fallback_generator(
                    story_title,
                    description,
                    acceptance_criteria,
                    affected_module,
                    roles,
                )

        st.subheader("Generated QA Test Cases")
        st.markdown(output)
        st.download_button(
            "Download Markdown",
            data=output,
            file_name="servicenow_qa_test_cases.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    render_app()
