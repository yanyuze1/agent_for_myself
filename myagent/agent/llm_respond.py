import os
import re
import httpx
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from functools import lru_cache
from dataclasses import dataclass
from skills.weather_skill import available_tools

# --- LLM客户端配置 ---
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"
PROMPT_FILE = ROOT_DIR / "prompts" / "agent_system.md"
@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model_id: str
    tavily_api_key: str
    proxy_url: str | None

def load_settings() -> Settings:
    load_dotenv(ENV_FILE)
    settings = Settings(
        api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
        model_id=os.getenv("OPENAI_MODEL_ID", "").strip(),
        tavily_api_key=os.getenv("TAVILY_API_KEY", "").strip(),
        proxy_url=os.getenv("OPENAI_PROXY_URL", "").strip() or None,
    )
    missing = [
        name for name, value in {
            "OPENAI_API_KEY": settings.api_key,
            "OPENAI_BASE_URL": settings.base_url,
            "OPENAI_MODEL_ID": settings.model_id,
            "TAVILY_API_KEY": settings.tavily_api_key,
        }.items() if not value
    ]
    if missing:
        raise ValueError(f".env 缺少配置: {', '.join(missing)}")
    os.environ.setdefault("TAVILY_API_KEY", settings.tavily_api_key)
    return settings

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str, api_key: str, base_url: str, proxy_url: str | None = None):
        self.model = model
        http_client = httpx.Client(proxy=proxy_url) if proxy_url else httpx.Client(trust_env=False)
        self.client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)


    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用模型并返回文本结果。"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content or ""

SETTINGS = load_settings()
AGENT_SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")
@lru_cache(maxsize=1)
def get_llm() -> OpenAICompatibleClient:
    return OpenAICompatibleClient(
        model=SETTINGS.model_id,
        api_key=SETTINGS.api_key,
        base_url=SETTINGS.base_url,
        proxy_url=SETTINGS.proxy_url,
    )

# llm输出解析相关的正则表达式
STEP_RE = re.compile(
    r"(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)",
    re.DOTALL,
)
ACTION_RE = re.compile(r"Action:\s*(.*)", re.DOTALL)
FINISH_RE = re.compile(r"^Finish\[(.*?)\]$", re.DOTALL)
TOOL_CALL_RE = re.compile(r"^(?P<tool>\w+)\((?P<args>.*)\)$", re.DOTALL)
KWARG_RE = re.compile(r'(\w+)="([^"]*)"')
def truncate_single_step(llm_output: str) -> str:
    match = STEP_RE.search(llm_output)
    if not match:
        return llm_output.strip()

    truncated = match.group(1).strip()
    if truncated != llm_output.strip():
        print("已截断多余的 Thought-Action 对")
    return truncated


def parse_action(llm_output: str) -> str:
    action_match = ACTION_RE.search(llm_output)
    if not action_match:
        raise ValueError("未能解析到 Action 字段。")
    return action_match.group(1).strip()


def parse_finish(action_str: str) -> str:
    finish_match = FINISH_RE.match(action_str)
    if not finish_match:
        raise ValueError("Finish 格式不正确。")
    return finish_match.group(1)


def parse_tool_call(action_str: str) -> tuple[str, dict[str, str]]:
    tool_call_match = TOOL_CALL_RE.match(action_str)
    if not tool_call_match:
        raise ValueError("Action 格式不正确，无法解析工具调用。")

    tool_name = tool_call_match.group("tool")
    args_str = tool_call_match.group("args")
    kwargs = dict(KWARG_RE.findall(args_str))
    return tool_name, kwargs

def execute_tool(tool_name: str, kwargs: dict[str, str]) -> str:
    if tool_name not in available_tools:
        return f"错误:未定义的工具 '{tool_name}'"
    return available_tools[tool_name](**kwargs)

def run_agent(user_prompt: str, max_steps: int = 5) -> str:
    prompt_history = [f"用户请求: {user_prompt}"]

    print(f"用户输入: {user_prompt}\n" + "=" * 40)

    for step in range(max_steps):
        print(f"--- 循环 {step + 1} ---\n")

        full_prompt = "\n".join(prompt_history)

        try:
            raw_output = get_llm().generate(
                full_prompt,
                system_prompt=AGENT_SYSTEM_PROMPT,
            )
        except Exception as e:
            return f"错误: 调用模型失败 - {e}"

        llm_output = truncate_single_step(raw_output)
        print(f"模型输出:\n{llm_output}\n")
        prompt_history.append(llm_output)

        try:
            action_str = parse_action(llm_output)
        except ValueError as e:
            observation_str = f"Observation: 错误: {e}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        if action_str.startswith("Finish"):
            try:
                final_answer = parse_finish(action_str)
            except ValueError as e:
                return f"错误: {e}"

            print(f"任务完成，最终答案: {final_answer}")
            return final_answer

        try:
            tool_name, kwargs = parse_tool_call(action_str)
        except ValueError as e:
            observation_str = f"Observation: 错误: {e}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        observation = execute_tool(tool_name, kwargs)
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)

    return "错误: 超过最大循环次数，任务未完成。"
