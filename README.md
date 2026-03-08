# ADK + LiteLLM + Skills Template

A template for building agents with [Google ADK](https://github.com/google/adk-python), [LiteLLM](https://github.com/BerriAI/litellm) proxy for multi-model routing, and ADK's native [Skills](https://google.github.io/adk-docs/skills/) system.

## Quick Start

### 1. Local Development (`adk web`)

The fastest path for iterating on agent code. Launches the ADK Web UI for interactive testing in your browser.

```bash
# Install
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Configure
cp .env.example .env    # fill in your keys + proxy URL

# Run
adk web .               # opens ADK web UI at http://localhost:8080
```

Open <http://localhost:8080> — select your agent from the dropdown, type a message, and start chatting.

### 2. Docker Debug (`adk web`)

Same interactive Web UI, running inside Docker. Useful for verifying the container works before deploying.

```bash
docker build -t adk-agent .

docker run --env-file .env -p 8080:8080 -e ADK_MODE=web adk-agent
```

Open <http://localhost:8080> to use the Web UI.

### 3. Production (`adk api_server`)

Headless REST API for programmatic access — what you deploy to prod. No UI; interact via `curl`, a custom frontend, or any HTTP client.

```bash
docker build -t adk-agent .

docker run --env-file .env -p 8080:8080 adk-agent
```

The API server starts on port 8080 (default `ADK_MODE=api`).

---

## API Reference (curl examples)

All examples assume the API server is running at `http://localhost:8080`.

### List available agents

```bash
curl http://localhost:8080/list-apps
```

### Create a session

Every conversation needs a session. The `userId` and `sessionId` can be any string you choose.

```bash
curl -X POST http://localhost:8080/apps/weather_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Send a message

```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "weather_agent",
    "userId": "u_123",
    "sessionId": "s_123",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    }
  }'
```

### Stream responses (SSE)

Server-Sent Events give you token-by-token streaming. Point an `EventSource` (browser) or `curl` at `/run_sse`:

```bash
curl -N -X POST http://localhost:8080/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "weather_agent",
    "userId": "u_123",
    "sessionId": "s_123",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": true
  }'
```

> `-N` disables curl's output buffering so you see events as they arrive.

### Delete a session

```bash
curl -X DELETE http://localhost:8080/apps/weather_agent/users/u_123/sessions/s_123
```

---

## Building a Frontend

The ADK API server is a standard REST/SSE backend. Here are some tips for connecting a custom UI.

### Minimal chat flow

1. **On page load** — call `POST /apps/{app}/users/{userId}/sessions/{sessionId}` with `{}` to create (or resume) a session.
2. **On send** — `POST /run_sse` with the user's message. Parse the SSE stream for agent responses.
3. **On close** — optionally `DELETE` the session, or keep it for conversation history.

### Parsing SSE events

Each SSE event is a JSON object. Look for events containing the agent's text response in `content.parts[].text`. A minimal JavaScript example:

```javascript
async function chat(appName, userId, sessionId, message) {
  const resp = await fetch("http://localhost:8080/run_sse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      appName,
      userId,
      sessionId,
      newMessage: { role: "user", parts: [{ text: message }] },
      streaming: true,
    }),
  });

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by double newlines
    const events = buffer.split("\n\n");
    buffer = events.pop(); // keep incomplete chunk

    for (const event of events) {
      const dataLine = event.split("\n").find((l) => l.startsWith("data: "));
      if (!dataLine) continue;
      const data = JSON.parse(dataLine.slice(6));
      // Extract text from the agent's response parts
      const parts = data?.content?.parts ?? [];
      for (const part of parts) {
        if (part.text) process.stdout.write(part.text); // or append to DOM
      }
    }
  }
}
```

### Tips

- **Session management** — Generate a unique `userId` per browser (e.g. `localStorage` UUID) and a new `sessionId` per conversation thread.
- **CORS** — If your frontend is on a different origin, you'll need to proxy requests or configure CORS on the server.
- **Non-streaming fallback** — Use `POST /run` instead of `/run_sse` if you don't need streaming. The response is a single JSON object.
- **Error handling** — Check for HTTP error status codes. The API returns JSON error bodies with details.

---

## Project Structure

```
adk-litellm-template/
├── weather_agent/                  # ADK agent package
│   ├── __init__.py                 # Entrypoint — exports root_agent
│   ├── agent.py                    # Agent definition + skills
│   └── skills/
│       ├── weather-skill/          # Example skill
│       │   ├── SKILL.md            # Skill metadata + instructions
│       │   ├── references/API.md   # Data format reference
│       │   └── assets/cities.json  # Mock weather data
│       └── search-skill/
│           ├── SKILL.md
│           └── references/PROVIDERS.md
├── Dockerfile
├── requirements.txt
└── .env.example
```

## How It Works

**LiteLLM Proxy** runs externally (you manage it separately). This agent points at it via `LITELLM_PROXY_API_BASE` in `.env`. The proxy handles routing to OpenAI, Anthropic, Gemini, or any other provider.

**ADK Skills** load incrementally to minimize context window usage:
- **L1** (name/description) — always loaded for discovery
- **L2** (instructions) — loaded when the skill is triggered
- **L3** (references/assets) — loaded on demand when referenced

## Switching Models

Change `DEFAULT_MODEL` in `.env` to any model your LiteLLM proxy serves (`curl http://litellm.overcastlab.com:4000/models -H 'Authorization: Bearer sk-1234'`)

## Adding a Skill

1. Create `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: One-line description for when to use this skill.
---

Step 1: Do something...
Step 2: Read 'references/GUIDE.md' for details.
Step 3: Return the result.
```

2. Load it in `agent.py`:

```python
my_skill = load_skill_from_dir(_SKILLS_DIR / "my-skill")
# Add to the SkillToolset skills list
```

## License

MIT
