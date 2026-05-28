# ServiceNow QA Test Case Generator Agent

A small Streamlit app that generates manual QA test cases for ServiceNow stories,
defects, and requirements.

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
3. Paste the token into the app sidebar, or set it as `HF_TOKEN`.
4. Use a model available through Hugging Face Inference Providers.

The default Hugging Face model is:

```text
Qwen/Qwen3-0.6B
```

If a Hugging Face provider returns `memory layout cannot be allocated`, use a
smaller model such as `Qwen/Qwen3-0.6B` or `HuggingFaceTB/SmolLM3-3B`.

For a local LLM, install [Ollama](https://ollama.com), pull a model, and select
**LangChain + local Ollama** in the app:

```powershell
ollama pull qwen3
streamlit run app.py
```

You can change the model in the sidebar.
