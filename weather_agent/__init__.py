"""ADK agent package — exports root_agent.

Used by:
  - a2a_app.py (A2A protocol server via uvicorn)
  - adk CLI tools (adk web / adk api_server) for local development
"""

from .agent import weather_agent

root_agent = weather_agent
