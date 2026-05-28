# Deployment

This Streamlit app can be hosted on Streamlit Community Cloud, Hugging Face
Spaces, Render, Railway, or any server that can run Python.

## Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to Streamlit Community Cloud and create a new app.
3. Select `app.py` as the main file.
4. Add `HF_TOKEN` in app secrets if you want Hugging Face inference.

Example Streamlit secret:

```toml
HF_TOKEN = "your_hugging_face_token_here"
```

## Hugging Face Spaces

1. Create a new Space.
2. Select Streamlit as the SDK.
3. Upload the files in this folder.
4. Add `HF_TOKEN` as a Space secret if needed.

## Render

Use this start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Notes

- Hosted Hugging Face inference requires a Hugging Face token.
- Local Ollama mode only works on a machine where Ollama is installed and running.
- The built-in free generator works without external services.
