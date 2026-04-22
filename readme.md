<h1 align="center">agent_for_myself</h1>

<p align="center">
  <img src="./images/agent_for_myself.jpeg" alt="agent_for_myself logo" width="420">
</p>

<p align="center">
  <strong>中文</strong> | <a href="./readme_EN.md">English</a>
</p>

## 项目简介

`agent_for_myself` 是一个简单的 Agent 项目仓库，核心目的就是用大量 AI 辅助来完成 Agent 的设计、实现、验证和迭代。

这个仓库不追求一开始就做成复杂平台，而是更强调：

- 用尽量小的成本搭出一个可运行的 Agent 闭环。
- 用 AI 辅助完成 Prompt 设计、工具接入和工作流程梳理。
- 保持结构简单，让后续继续扩展更容易。

## 这个仓库在做什么

当前仓库的主要代码位于 `myagent/` 目录中，它实现了一个轻量级的命令行 Agent Demo。

现阶段的示例场景是旅行助手，但它真正想表达的是更通用的 Agent 工作方式：

1. 接收用户输入。
2. 让模型根据系统提示词生成 `Thought` 和 `Action`。
3. 解析模型动作，判断是直接结束还是调用工具。
4. 把工具执行结果作为 `Observation` 回流给模型。
5. 重复推理，直到得到最终答案。

也就是说，这个仓库的重点不是“旅行”本身，而是“如何借助 AI 把一个最基础的 Agent 工作链路搭起来”。

## 当前特点

- 结构轻量，适合作为 Agent 入门和实验仓库。
- 使用 OpenAI 兼容接口，便于替换模型服务。
- 通过系统提示词约束模型按 `Thought + Action` 工作。
- 已经具备工具调用和结果回流的最小闭环。
- 很适合在 AI 辅助下持续迭代和扩展。

## 仓库结构

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

主要内容说明：

- `images/`：README 使用的项目图片。
- `readme.md` / `readme_EN.md`：仓库中英文介绍文档。
- `myagent/`：当前 Agent Demo 的主要实现目录。

## 快速开始

如果你想直接体验当前 Demo，可以进入 `myagent/` 目录后进行配置和运行。

### 1. 安装依赖

```bash
cd myagent
python3 -m pip install openai python-dotenv httpx requests tavily-python
```

### 2. 配置环境变量

在 `myagent/.env` 中至少配置：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_ID=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
OPENAI_PROXY_URL=
```

### 3. 运行

```bash
python3 user_request.py
```

然后输入你的任务，例如：

```text
我想这个周末去杭州，先帮我看看天气，再推荐几个适合当前天气的景点。
```

## 为什么适合做 Agent 起点

这个仓库很适合作为一个个人 Agent 起步项目，因为它：

- 足够简单，容易读懂和修改。
- 已经包含 Prompt、模型、工具、观察回流这些关键要素。
- 很适合和 AI 一起协作式开发，而不是从零搭一个大框架。
- 后续可以自然扩展到更多工具、更多任务和更复杂的流程。

## 后续可以继续扩展的方向

- 增加更多通用工具，而不局限于旅行场景。
- 把工具调用解析升级为更稳健的结构化方案。
- 增加测试、日志和依赖清单。
- 引入记忆、多任务拆解和更复杂的工作流。

## 总结

`agent_for_myself` 可以被理解为一个简单、清晰、适合持续迭代的 Agent 实验仓库。

它已经展示了一个最基础的 Agent 是如何工作的，也很适合作为“使用大量 AI 辅助完成 Agent 设计和工作”的个人实践起点。未来，这个仓库将作为Unitree Go2系列项目的基础 Agent 仓库，并继续迭代和扩展来实现一个更加智能的狗子！
