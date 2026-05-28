# ServiceNow QA Test Case Generator Agent

A small Streamlit app that generates manual QA test cases for ServiceNow stories,
defects, and requirements.

LLM-backed generation uses a two-pass flow: the model drafts test cases, then
reviews and improves coverage for positive, negative, boundary, edge, regression,
security, integration, and data validation scenarios before returning the final
answer.

Each generated test case is returned in plain English with only:

- Test Case
- Steps
- Expected Result

Steps begin with logging in to ServiceNow and going to the affected module or
table.

The app also checks input quality before generation and warns when details such
as acceptance criteria, roles, or module/table information are missing.

Generated test cases can be downloaded as `.xlsx` with these columns:

- Story#
- Test suite#
- Product
- Theme
- Test case description
- Short description
- Steps - always give detail steps
- Expected results

## Inputs

- Story title
- Description
- Acceptance criteria
- Affected module/table
- Roles involved

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## App Login

The app is password-protected by default. Configure these values in Streamlit
Cloud secrets:

```toml
APP_USERNAME = "your_username"
APP_PASSWORD = "your_strong_password"
APP_AUTH_ENABLED = "true"
```

Set `APP_AUTH_ENABLED = "false"` only for a trusted local or private deployment.

## Project Files

- `app.py` - Streamlit app and agent logic
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit hosting config
- `.env.example` - Example environment variables
- `DEPLOYMENT.md` - Hosting steps
- `render.yaml` - Optional Render deployment config

## Free generation options

The default **Built-in free generator** works without an API key.

For faster hosted inference, use **Hugging Face Inference API**:

1. Create a Hugging Face token with Inference Providers permission.
2. Install the requirements.
3. Add the token as `HF_TOKEN` in Streamlit secrets or an environment variable.
4. Use a model available through Hugging Face Inference Providers.

The default Hugging Face model is:

```text
Qwen/Qwen3-0.6B
```

If a Hugging Face provider returns `memory layout cannot be allocated`, use a
smaller model such as `Qwen/Qwen3-0.6B` or `HuggingFaceTB/SmolLM3-3B`.

The Hugging Face token is never shown in the app UI. Configure it through
Streamlit Cloud secrets for hosted deployments.

For a local LLM, install [Ollama](https://ollama.com), pull a model, and select
**LangChain + local Ollama** in the app:

```powershell
ollama pull qwen3
streamlit run app.py
```

You can change the model in the sidebar.
