"""Test A2A streaming endpoint.

Usage:
    1. Start the server:  uvicorn a2a_app:app --host 0.0.0.0 --port 8080
    2. Run this script:   python test_streaming.py
"""

import json
import uuid

import httpx

BASE_URL = "http://localhost:8080"


def test_agent_card():
    """Verify the agent card advertises streaming capability."""
    resp = httpx.get(f"{BASE_URL}/.well-known/agent.json")
    resp.raise_for_status()
    card = resp.json()
    streaming = card.get("capabilities", {}).get("streaming")
    print(f"Agent card streaming capability: {streaming}")
    assert streaming is True, "Streaming not enabled in agent card!"
    print("PASS: Agent card advertises streaming=true\n")


def test_non_streaming():
    """Send a regular message/send request (non-streaming baseline)."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "What is the weather in Tokyo?"}],
                "messageId": str(uuid.uuid4()),
            }
        },
    }

    print("--- Non-streaming test (message/send) ---")
    resp = httpx.post(f"{BASE_URL}/", json=payload, timeout=120.0)
    resp.raise_for_status()
    data = resp.json()
    print(json.dumps(data, indent=2))
    print()


def test_streaming():
    """Send a message/stream request and print SSE events as they arrive."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "What is the weather in Tokyo?"}],
                "messageId": str(uuid.uuid4()),
            }
        },
    }

    print("--- Streaming test (message/stream) ---")
    with httpx.stream("POST", f"{BASE_URL}/", json=payload, timeout=120.0) as resp:
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type')}")
        print()
        event_count = 0
        for line in resp.iter_lines():
            if line.startswith("data:"):
                event_count += 1
                data = json.loads(line[len("data:"):].strip())
                print(f"Event {event_count}:")
                print(json.dumps(data, indent=2))
                print()
        print(f"Total events received: {event_count}")


if __name__ == "__main__":
    test_agent_card()
    test_streaming()
