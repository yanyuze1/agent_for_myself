<h1 align="center">myagent</h1>

<p align="center">
  <img src="./images/myagent.jpeg" alt="myagent logo" width="420">
</p>

<p align="center">
  Language: <a href="./README.md">中文</a> | <a href="./README_EN.md">English</a>
</p>

`myagent` is a lightweight command-line travel assistant prototype. It connects user input, ReAct-style LLM reasoning, external tool calls, and final answer generation into a very readable end-to-end loop, which makes it a strong starting point for learning, demoing, and extending a minimal agent system.

## Preface

Based on the current code layout, this project appears to have been built in a pragmatic "make the full loop work first, then separate responsibilities" order:

1. Start with a thin CLI entry point in `user_request.py` to collect user input and print the final answer.
2. Move the core agent loop into `agent/llm_respond.py`, where configuration loading, model calls, output parsing, and tool execution are centralized.
3. Extract the system prompt into `prompts/agent_system.md` so the model is forced to follow a `Thought` plus `Action` protocol.
4. Keep concrete capabilities inside `skills/weather_skill.py` as callable tools.

The reason behind this structure is clear: the project is not trying to hide behavior behind a large framework. Instead, it aims to expose a small, understandable, debuggable, and extensible agent loop. For anyone learning how a user request becomes a model call, how the model chooses tools, and how tool results flow back into reasoning, this repository is a very useful example.

## Project Analysis

### 1. Project Structure

```text
myagent/
├── user_request.py
├── agent/
│   └── llm_respond.py
├── prompts/
│   └── agent_system.md
├── skills/
│   └── weather_skill.py
└── .env
```

Module responsibilities:

- `user_request.py`: CLI entry point. Reads input, calls `run_agent()`, and prints the final answer.
- `agent/llm_respond.py`: Core runtime. Loads `.env`, initializes the OpenAI-compatible client, runs the reasoning loop, parses model output, and executes tools.
- `prompts/agent_system.md`: System prompt. Enforces a strict one-step `Thought` and `Action` response format.
- `skills/weather_skill.py`: Tool layer. Currently provides weather lookup and attraction recommendation.

### 2. End-to-End Flow: From User Input to LLM Call to Output

The full execution path looks like this:

```text
User input
  -> user_request.py reads terminal text
  -> run_agent(user_prompt)
  -> prompt_history = ["用户请求: ..."]
  -> LLM generates Thought/Action using system prompt + history
  -> Parse Action
     -> If Finish[final answer], stop
     -> If tool_name(...), execute the matching tool
  -> Wrap tool result as Observation
  -> Append Observation back into prompt_history
  -> Continue the next reasoning round
  -> Return and print the final answer
```

In more detail:

1. The user enters a request in the terminal.
2. `user_request.py` calls `run_agent(user_prompt)`.
3. `run_agent()` initializes `prompt_history` with `用户请求: ...`.
4. `get_llm().generate()` sends the system prompt plus the accumulated history to the model.
5. The model must reply in a strict format such as:

```text
Thought: I should check the weather first
Action: get_weather(city="Hangzhou")
```

6. The program parses the `Action` line with regular expressions:
   - If it is `Finish[...]`, the task ends immediately.
   - If it is a tool call, the tool name and arguments are extracted.
7. `execute_tool()` looks up the tool in `available_tools` and runs it.
8. The tool result is wrapped as `Observation: ...` and appended to `prompt_history`.
9. The next model turn sees the original user request, prior reasoning, prior action, and the new observation.
10. Once the model returns `Action: Finish[...]`, the program prints the final answer and exits.

### 3. Important Design Choices in the Current Implementation

- This is a classic ReAct-style single-step loop. The system prompt explicitly forces the model to produce only one `Thought` and one `Action` at a time.
- `truncate_single_step()` defensively trims extra `Thought/Action` pairs in case the model outputs too much at once.
- `OpenAICompatibleClient` is intentionally vendor-agnostic as long as the endpoint follows the OpenAI API style.
- `load_settings()` runs during module import, which means missing environment variables fail early instead of failing later during a model request.
- `prompt_history` is maintained as plain text. That keeps the implementation simple, but it does not provide structured conversation state management.
- The project currently exposes only two tools, so this repository should be seen as an agent skeleton rather than a full travel platform.

### 4. How the Tool Layer Actually Works

The current tool set contains only two capabilities:

- `get_weather(city: str)`: Queries `wttr.in` for real-time weather and returns weather description plus Celsius temperature.
- `get_attraction(city: str, weather: str)`: Uses Tavily Search to recommend attractions for a city under the given weather condition.

That means the runtime depends on more than just an LLM:

- An accessible OpenAI-compatible model endpoint.
- A valid Tavily API key.
- Network access to both `wttr.in` and Tavily services.

### 5. Strengths and Current Boundaries

Strengths:

- Small codebase and low reading cost.
- Highly transparent input-to-output pipeline, ideal for debugging and teaching.
- The core loop of "reason -> act -> observe -> reason again" is already working.
- Better portability than a single hard-coded provider because it supports OpenAI-compatible endpoints.

Boundaries:

- It only targets travel use cases, with weather and attraction recommendation as the current scope.
- Tool parsing only supports keyword arguments in the form `key="value"`.
- There is no test suite, dependency manifest, `.env.example`, log level control, or layered exception handling yet.
- Context is managed by string concatenation, which becomes limiting for more complex tasks.
- `max_steps` defaults to 5, so longer workflows may terminate early.

## Project Configuration

### 1. Runtime Requirements

Based on the current source code, the recommended environment is:

- `Python 3.10+`
- Network access
- Reachability to an OpenAI-compatible endpoint and Tavily

### 2. Install Dependencies

The repository does not currently include a `requirements.txt` or `pyproject.toml`, so dependencies need to be installed manually. Based on the imports in source code, at least the following packages are required:

```bash
python3 -m pip install openai python-dotenv httpx requests tavily-python
```

You can also install dependencies with reference to the [hello_agent](https://hello-agents.datawhale.cc/#/./chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93) project.

If the `tavily` module still cannot be imported in your environment, make sure the correct Tavily Python SDK is installed.

### 3. Configure `.env`

The project reads `.env` from the repository root. Required and optional variables are:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_ID=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
OPENAI_PROXY_URL=
```

Variable meanings:

- `OPENAI_API_KEY`: API key for the model provider.
- `OPENAI_BASE_URL`: Base URL of an OpenAI-compatible endpoint.
- `OPENAI_MODEL_ID`: Model name to call.
- `TAVILY_API_KEY`: Tavily key used for attraction search.
- `OPENAI_PROXY_URL`: Optional proxy URL. Leave empty if you do not need one.

Configuration notes:

- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_ID`, and `TAVILY_API_KEY` are mandatory. Missing any of them will cause the program to fail during startup.
- `TAVILY_API_KEY` is also copied into the process environment for tool access.
- Real secrets in `.env` should never be committed to a public repository.

## Usage

### 1. Recommended Usage Sequence

Use the project in this order:

1. Install dependencies.
2. Configure `.env` in the project root.
3. Run:

```bash
python3 user_request.py
```

4. Enter a clear travel-related prompt, for example:

```text
I want to visit Hangzhou this weekend. Please check the weather first and then recommend attractions suitable for that weather.
```

5. The program will print intermediate reasoning steps and the final answer.

### 2. What Kind of Prompts Work Best Right Now

The current project works best for:

- Weather lookup for a specific city.
- Attraction recommendations based on weather.
- Single-city, single-topic travel questions with a short reasoning chain.

Better prompts usually:

- Explicitly name the city.
- State the full intent, such as "check the weather, then recommend attractions."
- Avoid multi-city, multi-day, or highly constrained requests in one shot.

### 3. What You Will See at Runtime

By default, the terminal output includes:

- The original user input
- The current loop number
- The raw model output
- Tool execution results as `Observation`
- The final answer

That makes the project especially useful for debugging because you can directly inspect how the model decided to call a tool.

### 4. Common Issues

If the project fails, check these first:

- `ModuleNotFoundError: No module named 'openai'`
  - Dependencies are not fully installed.
- `.env 缺少配置`
  - One or more required environment variables are missing.
- `错误: 调用模型失败`
  - The model endpoint is unreachable, the key is invalid, the proxy is misconfigured, or the endpoint is not compatible.
- `错误:查询天气时遇到网络问题`
  - `wttr.in` is unreachable or the network is unstable.
- `错误:执行Tavily搜索时出现问题`
  - There is an issue with Tavily credentials or network access.

## Epilogue

The value of `myagent` is not that it already does everything. Its value is that it already proves the most important agent loop end to end. For understanding tool-using agents, this is a very solid starting point.

If this project continues to evolve, a practical next roadmap would be:

- Add `requirements.txt` or `pyproject.toml` to simplify setup.
- Add `.env.example` for safer and clearer configuration.
- Replace regex-based parsing with a more robust structured tool-calling approach.
- Add logging, tests, and clearer error boundaries.
- Expand travel capabilities such as hotel suggestions, route planning, budget guidance, and food recommendations.
- Add multi-turn memory and better context management.
- Evolve the current CLI version into an API service or web application.

If you treat this repository as a verifiable, explainable, and extensible minimal agent foundation, it has already achieved a very meaningful first milestone.
