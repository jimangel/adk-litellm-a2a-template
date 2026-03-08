FROM python:3.11-slim

WORKDIR /app

RUN adduser --disabled-password --gecos "" agentuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=agentuser:agentuser . .

USER agentuser
ENV PATH="/home/agentuser/.local/bin:$PATH"

ENV PORT=8080
ENV ADK_MODE=api
EXPOSE ${PORT}

# ADK_MODE=api  → REST API server (default, for deployment + curl testing)
# ADK_MODE=web  → Web UI (for local dev/debug)
CMD if [ "$ADK_MODE" = "web" ]; then \
      adk web --port=${PORT} --host=0.0.0.0 "/app"; \
    else \
      adk api_server --port=${PORT} --host=0.0.0.0 "/app"; \
    fi
