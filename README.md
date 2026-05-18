# Engineering Intelligence Agent
### Agentic AI for Engineering Document Analysis & Reporting

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://langchain-ai.github.io/langgraph/)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4o-0078D4?logo=microsoft-azure)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C)](https://langchain.com)

---

## Overview

An **agentic AI system** that autonomously answers complex engineering queries by reasoning across multiple tools — retrieving domain documents, performing Eurocode calculations, assessing project risks, and compiling professional engineering reports.


```
User Query (natural language)
        │
        ▼
┌───────────────────┐
│   LangGraph Agent │  ←── Azure OpenAI GPT-4o
│   (ReAct loop)    │
└────────┬──────────┘
         │  Autonomously decides which tools to call and in what order
         ▼
┌────────────────────────────────────────────────────────┐
│  Tool 1: search_engineering_documents                  │
│           → RAG retrieval from engineering knowledge   │
│             base (Eurocode, BS standards, notes)   │
├────────────────────────────────────────────────────────┤
│  Tool 2: calculate_engineering_metric                  │
│           → Eurocode load combinations, bearing        │
│             capacity, safety factors, embodied carbon  │
├────────────────────────────────────────────────────────┤
│  Tool 3: classify_risk_level                           │
│           → 5×5 risk matrix with required actions      │
│             and recommended mitigations                │
├────────────────────────────────────────────────────────┤
│  Tool 4: generate_structured_report                    │
│           → Formal format engineering report       │
└────────────────────────────────────────────────────────┘
        │
        ▼
  Structured Engineering Report (saved to /output)
```

---

## Architecture

```
engineering-intelligence-agent/
│
├── main.py                     # Entry point — interactive + CLI modes
│
├── agent/
│   ├── graph.py                # LangGraph StateGraph — the agent loop
│   ├── tools.py                # 4 tools the agent can call
│   ├── azure_client.py         # Azure OpenAI connection
│   └── prompts.py              # System prompt (agent's constitution)
│
├── data/
│   ├── knowledge_base.py       # In-memory RAG (upgradeable to Azure AI Search)
│   └── sample_docs.py          # Engineering standards knowledge base
│
├── output/                     # Generated reports saved here
├── requirements.txt
├── .env.example                # Credential template
└── README.md
```

---

## Key Technical Concepts

### 1. Agentic AI with LangGraph
The agent uses the **ReAct (Reason + Act)** pattern. Rather than following a fixed workflow, the LLM:
1. **Reasons** about what information it needs
2. **Acts** by calling a tool
3. **Observes** the tool's result
4. **Reasons again** — repeating until it has enough information to answer

LangGraph models this as a **directed graph** where nodes are LLM calls or tool executions, and edges are control flow. This gives explicit control over:
- Retry logic
- Conditional branching
- Human-in-the-loop approval gates
- Parallel tool execution

### 2. RAG (Retrieval-Augmented Generation)
Rather than relying on the LLM's training data (which may be outdated or lack proprietary standards), the agent **retrieves relevant document chunks** from the knowledge base before answering.

**Prototype:** Keyword-based relevance scoring  
**Production upgrade:** Azure AI Search with vector embeddings from `text-embedding-3-large`

### 3. Tool Calling / Function Calling
Tools are Python functions decorated with `@tool`. The LLM outputs structured JSON describing the tool name and arguments. LangGraph's `ToolNode` executes the actual Python function and returns the result into the message stream.

The LLM never executes code directly — it outputs *intent*, Python executes *action*.

### 4. Azure OpenAI Integration
Uses `AzureChatOpenAI` from `langchain-openai`, pointing to a GPT-4o deployment on Azure OpenAI Service.

**Production security pattern:**
- No API keys in code — credentials via environment variables
- For production: Azure Managed Identity (no secrets at all)
- All traffic over HTTPS to private Azure endpoint

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Azure subscription with Azure OpenAI access
- Azure OpenAI resource with GPT-4o deployed

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/engineering-intelligence-agent.git
cd engineering-intelligence-agent
```

### Step 2 — Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Azure credentials
```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:
```env
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

> **Where to find credentials:**  
> Azure Portal → Your OpenAI Resource → Keys and Endpoint

### Step 5 — Run the agent
```bash
# Interactive mode (recommended for first run)
python main.py

# Run a specific demo query
python main.py --demo 1

# Pass a custom query directly
python main.py --query "Assess the structural risks of a pedestrian bridge on soft ground" --project "Bridge Assessment"
```

---

## Demo Queries

| # | Title | Tools Used |
|---|-------|-----------|
| 1 | Foundation design on soft clay | Search + Calculate + Risk + Report |
| 2 | Pedestrian footbridge load assessment | Calculate + Search + Risk + Report |
| 3 | Urban tunnel risk assessment | Search + Risk + Report |
| 4 | Net zero carbon estimate | Calculate + Search + Report |

---

## Production Upgrade Path

| Component | Prototype | Production (Azure) |
|---|---|---|
| Document retrieval | Keyword search in-memory | Azure AI Search (hybrid vector + keyword) |
| Document embeddings | N/A | Azure OpenAI `text-embedding-3-large` |
| LLM | Azure OpenAI (API key) | Azure OpenAI (Managed Identity) |
| Hosting | Local Python | Azure Container Apps |
| Monitoring | Console logs | Azure Application Insights |
| Secrets | .env file | Azure Key Vault |
| Orchestration | LangGraph local | LangGraph + Azure Prompt Flow |
| Throughput | Standard tier | Provisioned Throughput Units (PTU) |

---

## Author

**Haroun Abdul Azis**  
AI Solutions Specialist | Pre-Sales  
Cambridge, UK  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://linkedin.com/in/YOUR-LINKEDIN)

---

## Licence

MIT — free to use, adapt, and build upon with attribution.
