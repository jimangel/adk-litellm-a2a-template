"""A2A entrypoint — exposes the weather agent via the Agent-to-Agent protocol."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

from a2a.server.apps import A2AStarletteApplication  # noqa: E402
from a2a.server.request_handlers import DefaultRequestHandler  # noqa: E402
from a2a.server.tasks import InMemoryPushNotificationConfigStore  # noqa: E402
from a2a.server.tasks import InMemoryTaskStore  # noqa: E402
from a2a.types import AgentCapabilities  # noqa: E402
from starlette.applications import Starlette  # noqa: E402

from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor  # noqa: E402
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder  # noqa: E402
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService  # noqa: E402
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService  # noqa: E402
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions.in_memory_session_service import InMemorySessionService  # noqa: E402
from weather_agent import root_agent  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
port = int(os.getenv("PORT", "8080"))

adk_logger = logging.getLogger("google_adk")
adk_logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# A2A components (mirrors to_a2a() but adds streaming capability)
# ---------------------------------------------------------------------------
async def _create_runner() -> Runner:
    return Runner(
        app_name=root_agent.name or "adk_agent",
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
    )


task_store = InMemoryTaskStore()
agent_executor = A2aAgentExecutor(runner=_create_runner)
request_handler = DefaultRequestHandler(
    agent_executor=agent_executor,
    task_store=task_store,
    push_config_store=InMemoryPushNotificationConfigStore(),
)

card_builder = AgentCardBuilder(
    agent=root_agent,
    rpc_url=f"http://0.0.0.0:{port}/",
    capabilities=AgentCapabilities(streaming=True),
)

# ---------------------------------------------------------------------------
# Starlette app with A2A routes added at startup
# ---------------------------------------------------------------------------
app = Starlette()


async def _setup_a2a():
    agent_card = await card_builder.build()
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    a2a_app.add_routes_to_app(app)


app.add_event_handler("startup", _setup_a2a)
