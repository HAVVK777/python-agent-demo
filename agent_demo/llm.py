import httpx
from protocol import BaseAdapter, Message, LLMResponse, ToolSchema

class LLMClient:
    def __init__(self,
        adapter:BaseAdapter,
        base_url:str,
        api_key:str,
        model:str,
        timeout:int = 60
    ):
        self.adapter = adapter
        self.base_url = base_url      # 由调用方指定，不硬编码在 adapter 中
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def chat(self, messages:list[Message], tools:list[ToolSchema] | None = None)->LLMResponse:
        body = self.adapter.build_request(self.model, messages, tools)
        headers = self.adapter.get_headers()
        if not headers:
            headers["Authorization"] = "Bearer " + self.api_key  # Bearer 后面必须带空格
        else:
            for k, v in headers.items():
                if v is None:
                    headers[k] = self.api_key
                else:
                    headers[k] = v
        headers["Content-Type"] = "application/json"

        # 拼接完整 URL：base_url + endpoint
        url = self.base_url + self.adapter.get_endpoint()
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers,json=body)
            resp.raise_for_status()
            return self.adapter.parse_response(resp.json())
