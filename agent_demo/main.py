from protocol import Message
from llm import LLMClient
from agent import Agent
from adapters.openai_adapter import OpenAIAdapter



def main():
    # ============================================================
    # 配置：换厂商只需改这两行
    # ============================================================
    adapter = OpenAIAdapter()                       # 或用 AnthropicAdapter()
    base_url = "https://api.deepseek.com/v1"        # 或 https://api.openai.com/v1
    api_key  = "sk-fdca2f403598499a84bcfc25be408d0c"
    model    = "deepseek-chat"

    llm = LLMClient(
        adapter=adapter,
        base_url=base_url,
        api_key=api_key,
        model=model,
    )

    agent = Agent(
        llm=llm,
        system_prompt="你是友好的助手，用中文回答，简洁清晰。",
        max_rounds=10,
    )

    messages: list[Message] = []
    print("Agent 就绪，输入 exit 退出\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("再见！")
            break

        messages.append(Message(role="user", content=user_input))
        reply = agent.invoke(messages)
        messages.append(Message(role="assistant", content=reply))

        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()