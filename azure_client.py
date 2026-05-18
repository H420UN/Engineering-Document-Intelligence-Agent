"""
azure_client.py
───────────────
Handles the connection to Azure OpenAI Service.
Uses environment variables so credentials are NEVER hardcoded.

WHAT THIS DOES:
- Reads your Azure credentials from a .env file
- Returns a configured LLM object that LangGraph's agent node uses
- Uses AzureChatOpenAI from langchain_openai — this is the Azure-native
  wrapper around OpenAI's chat endpoint

INTERVIEW TALKING POINT:
  "I used Managed Identity in production but for this prototype I used
   API key auth via environment variables, which is the standard
   approach for local development and CI/CD pipelines."
"""

import os
from langchain_openai import AzureChatOpenAI


def get_llm(temperature: float = 0.1) -> AzureChatOpenAI:
    """
    Initialise and return the Azure OpenAI Chat model.

    Args:
        temperature: Controls randomness. 0.1 = focused/deterministic,
                     which is what we want for technical engineering answers.

    Returns:
        AzureChatOpenAI: A LangChain-compatible LLM instance bound to
                         your Azure OpenAI deployment.
    """
    return AzureChatOpenAI(
        # ── Replace these in your .env file ──────────────────────────────────
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        # ─────────────────────────────────────────────────────────────────────
        temperature=temperature,
        max_tokens=2000,
        # Streaming can be enabled for real-time token output in a UI
        streaming=False,
    )
