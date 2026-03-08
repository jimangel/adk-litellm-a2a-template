"""A2A entrypoint — exposes the weather agent via the Agent-to-Agent protocol."""

from dotenv import load_dotenv

load_dotenv()

from weather_agent import root_agent  # noqa: E402
from google.adk.a2a.utils.agent_to_a2a import to_a2a  # noqa: E402

app = to_a2a(root_agent)
