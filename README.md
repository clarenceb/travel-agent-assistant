# Travel Agent Assistant

## Setup

- Create an Azure AI Foundry Project
- Add a `gpt-4o` model deployment
- Create an agent
- Set the system prompt for the agent, see [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md)
- Add the knowledge tool: Grounding with Bing Search
- Add the action tool: Logic App (create the logic app resource using [`logic-app.json`](./logic-app.json))
  - See [LOGIC_APP_TOOL.md](LOGIC_APP_TOOL.md) for setup steps

## Demo Script

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

## (Optional) UI Interface

```sh
python -mvenv .venv
source .venv/bin/activate
pip install streamlit azure-ai-projects azure-ai-agents azure-identity

cp .env-template .env
# Edit .env file with your project, agent id, and LLM deployment settings

streamlit run app.py
```
