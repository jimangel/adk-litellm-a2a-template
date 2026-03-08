---
name: weather-skill
description: >
  Retrieves current weather information for cities worldwide. Use this skill
  when the user asks about weather conditions, temperature, or forecasts for
  a specific location.
---

## Weather Lookup Instructions

Follow these steps when the user asks about weather:

### Step 1 — Identify the city

Extract the city name from the user's request. If the city is ambiguous
(e.g. "Springfield"), ask the user to clarify.

### Step 2 — Check supported cities

Read `assets/cities.json` for the list of supported cities and their
weather data. If the requested city is in the list, return its report.

### Step 3 — Handle unsupported cities

If the city is not in the supported list, let the user know and suggest
they try one of the supported cities.

### Step 4 — Format the response

Present weather clearly:
- Lead with the city name and current conditions
- Include temperature (both °C and °F)
- Mention humidity and any notable conditions

See `references/API.md` for the data format reference.
