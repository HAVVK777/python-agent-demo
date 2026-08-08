from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class Message:
    role:str
    content:str = ""
    tool_call_id:str=""

@dataclass
class AssistantMessage(Message):
    tool_calls:list["ToolCall"] = field(default_factory=list)

@dataclass
class ToolCall:
    id:str
    name:str
    arguments:dict

@dataclass
class ToolResult:
    call_id:str
    name:str
    output:str

@dataclass
class LLMResponse:
    content:str = ""
    tool_calls:list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self)->bool:
        return len(self.tool_calls) > 0

@dataclass
class ToolSchema:
    name:str
    description:str
    parameters:dict

class BaseAdapter(ABC):

    @abstractmethod
    def build_request(
        self,
        model:str,
        messages:list[Message],
        tools:list[ToolSchema] | None = None
    )->dict:
        pass

    @abstractmethod
    def parse_response(self,raw:dict)->LLMResponse:
        pass

    @abstractmethod
    def get_headers(self)->dict:
        pass

    @abstractmethod
    def get_endpoint(self)->str:
        """返回 chat completion 端点路径，例如 /chat/completions"""
        pass


