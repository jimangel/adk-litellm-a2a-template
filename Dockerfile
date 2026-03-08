FROM python:3.11-slim

WORKDIR /app

RUN adduser --disabled-password --gecos "" agentuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=agentuser:agentuser . .

USER agentuser
ENV PATH="/home/agentuser/.local/bin:$PATH"

ENV PORT=8080
EXPOSE ${PORT}

CMD uvicorn a2a_app:app --host=0.0.0.0 --port=${PORT}
