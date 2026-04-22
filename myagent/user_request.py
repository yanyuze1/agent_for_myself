from agent.llm_respond import run_agent

def main() -> None:
    user_prompt = input("请输入你的请求：").strip()
    if not user_prompt:
        print("错误: 用户输入不能为空。")
        return

    final_answer = run_agent(user_prompt)
    print("\n最终结果:")
    print(final_answer)


if __name__ == "__main__":
    main()
