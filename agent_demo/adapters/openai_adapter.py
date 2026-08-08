import json
from protocol import (BaseAdapter, Message, AssistantMessage,
                      LLMResponse,ToolCall,ToolSchema
)

class OpenAIAdapter(BaseAdapter):

    def _to_openai_tool(self, t:ToolSchema)->dict:
        return {
            "type":"function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
        }

    def _to_openai_msg(self, m:Message)->dict:
        msg:dict = {"role": m.role, "content":m.content}

        # tool 消息需要带回 tool_call_id
        if m.role == "tool" and m.tool_call_id:
            msg["tool_call_id"] = m.tool_call_id

        # assistant 带 tool_calls
        if isinstance(m, AssistantMessage) and m.tool_calls:
            msg["tool_calls"] = []
            for tc in m.tool_calls:
                msg["tool_calls"].append({
                    "id" : tc.id,
                    "type": "function",
                    "function":{
                        "name":tc.name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False)
                    }
                })
        return msg

    def build_request(
        self, model:str,
        messages:list[Message], tools:list[ToolSchema] | None = None):
        body:dict = {
            "model":model,
            "messages":[self._to_openai_msg(m) for m in messages],
            "max_tokens":10240,
            "temperature":0.0
        }
        if tools:
            body["tools"] = [self._to_openai_tool(t) for t in tools]
        return body

    def parse_response(self, raw:dict)->LLMResponse:
        choice = raw["choices"][0]
        msg = choice["message"]

        tool_calls = []
        for tc in msg.get("tool_calls") or []:
            tool_calls.append(ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"])
            ))
        return LLMResponse(
            content=msg.get("content") or "",
            tool_calls=tool_calls
        )

    def get_headers(self):
        return {}

    def get_endpoint(self):
        return "/chat/completions"
