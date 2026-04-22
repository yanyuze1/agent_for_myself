<h1 align="center">agent_for_myself</h1>

<p align="center">
  <img src="./images/agent_for_myself.jpeg" alt="agent_for_myself logo" width="420">
</p>

<p align="center">
  <a href="./readme.md">中文</a> | <strong>English</strong>
</p>

## Overview

`agent_for_myself` is a simple Agent repository whose main purpose is to use heavy AI assistance to design, build, validate, and iterate on Agent workflows.

Instead of trying to become a large platform from the start, this repository focuses on:

- Building a runnable Agent loop with as little overhead as possible.
- Using AI to help with prompt design, tool integration, and workflow shaping.
- Keeping the structure simple so future expansion stays easy.

## What This Repository Does

The main code currently lives in the `myagent/` directory, where a lightweight command-line Agent demo is implemented.

The current demo scenario is a travel assistant, but the broader idea is a general Agent workflow:

1. Accept user input.
2. Let the model generate `Thought` and `Action` based on the system prompt.
3. Parse the model action to decide whether to finish or call a tool.
4. Feed tool results back as `Observation`.
5. Continue reasoning until the final answer is produced.

In other words, the real focus of this repository is not the travel domain itself, but how to build a minimal Agent workflow with strong AI assistance.

## Current Highlights

- Lightweight structure, good for Agent learning and experimentation.
- Uses an OpenAI-compatible API, which makes model replacement easier.
- Constrains the model with a `Thought + Action` prompt pattern.
- Already includes a minimal loop for tool calling and observation feedback.
- A strong starting point for continuous AI-assisted iteration.

## Repository Structure

```text
agent_for_myself/
├── readme.md
├── readme_EN.md
├── images/
│   └── myagent.jpeg
└── myagent/
    ├── user_request.py
    ├── agent/
    │   └── llm_respond.py
    ├── prompts/
    │   └── agent_system.md
    ├── skills/
    │   └── weather_skill.py
    └── ...
```

Main parts:

- `images/`: Image assets used in the README files.
- `readme.md` / `readme_EN.md`: Chinese and English repository introductions.
- `myagent/`: Main implementation directory for the current Agent demo.

## Quick Start

If you want to try the current demo, enter the `myagent/` directory and run it from there.

### 1. Install Dependencies

```bash
cd myagent
python3 -m pip install openai python-dotenv httpx requests tavily-python
```

### 2. Configure Environment Variables

Set at least the following values in `myagent/.env`:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_ID=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
OPENAI_PROXY_URL=
```

### 3. Run

```bash
python3 user_request.py
```

Then enter a task such as:

```text
I want to visit Hangzhou this weekend. Please check the weather first and then recommend a few attractions suitable for the current weather.
```

## Why It Works Well As a Starting Point

This repository works well as a personal Agent starter project because it is:

- Simple enough to read and modify quickly.
- Complete enough to include prompts, model calls, tool usage, and observation feedback.
- Well suited for building together with AI instead of starting with a large framework.
- Easy to extend into more tools, more tasks, and richer workflows.

## Natural Next Steps

- Add more general tools beyond the current travel example.
- Replace the tool parser with a more robust structured approach.
- Add tests, logging, and a dependency manifest.
- Introduce memory, task decomposition, and more complex workflows.

## Summary

`agent_for_myself` can be understood as a simple, clear, and extendable Agent experiment repository.

It already shows how a minimal Agent works end to end, and it is a solid personal starting point for using AI assistance to design and execute Agent work.
