"""Weather Agent — uses ADK Skills + LiteLLM proxy + Windmill MCP."""

import os
import pathlib
import litellm

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# ---------------------------------------------------------------------------
# Load skills
# ---------------------------------------------------------------------------
_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

weather_skill = load_skill_from_dir(_SKILLS_DIR / "weather-skill")
search_skill = load_skill_from_dir(_SKILLS_DIR / "search-skill")

skills_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill, search_skill],
)

# ---------------------------------------------------------------------------
# MCP via LiteLLM Proxy
# ---------------------------------------------------------------------------
windmill_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://litellm.overcastlab.com:4000/windmill_mcp/mcp",
        headers={"Authorization": f"Bearer {os.getenv('LITELLM_PROXY_API_KEY', '')}"},
    ),
    # Optional: filter to specific tools if needed
    # tool_filter=["some_tool", "another_tool"],
)

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
model_str = os.getenv("DEFAULT_MODEL", "gpt-5.2")
litellm.use_litellm_proxy = True

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
weather_agent = Agent(
    name="weather_agent",
    model=LiteLlm(model=model_str),
    description="An assistant with weather, search, and Windmill skills.",
    instruction=(
        "You are a helpful assistant with access to specialized skills.\n\n"
        "Available skills:\n"
        "- **weather_skill** — Look up current weather for cities.\n"
        "- **search_skill** — Search the web for general information.\n"
        "- **Windmill MCP tools** — Interact with Windmill workflows.\n\n"
        "Use the appropriate skill based on the user's request. If a skill "
        "returns an error, let the user know and suggest alternatives."
    ),
    tools=[skills_toolset, windmill_mcp],
)