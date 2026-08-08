from protocol import Message, AssistantMessage, ToolResult
from tools import get_all_schemas, run
from llm import LLMClient

class Agent:
    def __init__(self,llm:LLMClient,system_prompt:str = "", max_rounds:int=10):
        self.llm=llm
        self.system_prompt = system_prompt
        self.max_rounds = max_rounds
        self.tools = get_all_schemas()

    def _handle_tool_calls(self,messages:list[Message],resp):
        messages.append(AssistantMessage(role="assistant",content=resp.content,tool_calls=resp.tool_calls))
        for tc in resp.tool_calls:
            
            output=run(tc.name, tc.arguments)
            messages.append(Message(role="tool", content=output, tool_call_id=tc.id))

    def invoke(self,messages:list[Message])->str:
        full = []
        if self.system_prompt:
            full.append(Message(role="system",content=self.system_prompt))
        full.extend(messages)
        for _ in range(self.max_rounds):
            resp = self.llm.chat(full, self.tools)
            if not resp.has_tool_calls:
                return resp.content

            self._handle_tool_calls(messages=full,resp=resp)
        return "已到达最大循环数"
