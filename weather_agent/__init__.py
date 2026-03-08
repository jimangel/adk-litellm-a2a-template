"""ADK entrypoint — exports root_agent for `adk web .` discovery."""

from .agent import weather_agent

root_agent = weather_agent
