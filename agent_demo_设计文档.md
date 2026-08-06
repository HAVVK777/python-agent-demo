# 【文档标题:例如「小型 Python Agent 示例设计文档」】

> **使用说明**
>
> 本文档是模板,所有以【】包裹的内容都需要你自行替换为自定义内容。
> 文档按模块组织,每个模块包含:**模块职责说明 + 代码示例**。
> 代码示例直接调用大模型的 HTTP 接口(使用 `requests` 库),不依赖任何厂商 SDK;示例按 OpenAI 兼容接口格式编写(DeepSeek 即此格式)。如需更换其他大模型供应商,通常只需要修改「4.1 配置模块」与「4.2 大模型接口模块」。
> 你可以自由增删章节、修改标题、调整顺序,以下仅为参考骨架。

---

## 1. 项目概述

- 项目名称:【自定义项目名称】
- 一句话介绍:【用一句话说明这是一个什么样的 Agent,例如「一个可以调用外部工具完成某某任务的助手」】
- 项目定位:【说明做这个示例的目的,例如「学习 Agent 的基本组成」「演示某某场景」】

## 2. 目标与范围

### 2.1 目标

- 【目标一:例如「实现一个能回答某某领域问题的问答 Agent」】
- 【目标二:例如「演示 Agent 如何调用工具获取实时信息」】
- 【目标三:如有更多请继续添加】

### 2.2 非目标(明确不做的事)

- 【例如「不做多轮对话记忆」「不做复杂多 Agent 协作」】
- 【例如「不考虑生产环境部署与性能优化」】

## 3. Agent 核心概念说明

> 说明:请用你自己的理解改写本节,以下结构仅供参考。

- Agent 是什么:【用你自己的话定义,例如「Agent 是一个由大模型驱动的、可以自主决定调用哪些工具来完成任务的程序」】
- 核心组成部分(与第 4 章的模块一一对应):
  - 【组件一:例如「大模型接口模块(llm.py)」——负责理解用户意图、生成回复】
  - 【组件二:例如「工具模块(tools.py)」——Agent 可以调用的外部能力,如【自定义工具名】】
  - 【组件三:例如「配置模块(config.py)」——集中管理模型名、API Key、轮次上限等】
  - 【组件四:例如「主程序(agent_demo.py)」——「思考 → 调用工具 → 观察结果 → 继续思考」的运行循环】

## 4. 模块设计与代码示例

> 说明:以下每个小节对应一个模块,「模块职责」部分可自定义,「代码示例」部分可直接作为开发参考。
> 代码中的【】同样表示需要你替换的内容(如模型名、工具名、系统提示词等)。

### 4.1 配置模块 config.py

**模块职责**:【自定义说明,例如「集中管理所有可配置项:API Key、接口地址、模型名称、最大工具调用轮数、系统提示词;修改配置时不需要改动其他模块」】

**代码示例**:

```python
"""【模块说明:例如「集中管理所有可配置项,方便修改」】"""

import os

# 【自定义:你的 API Key 所在的环境变量名,不要把 Key 直接写在这里】
API_KEY_ENV = "DEEPSEEK_API_KEY"

# 【自定义:大模型 HTTP 接口地址;更换供应商时同步修改这里与 4.2 的请求头】
API_BASE_URL = "https://api.deepseek.com"

# 【自定义:模型名称,例如 deepseek-chat / deepseek-reasoner】
MODEL_NAME = "【模型名称,例如 deepseek-chat】"

# 【自定义:单次问答中最多允许调用几次工具,防止 Agent 陷入死循环】
MAX_TOOL_ROUNDS = 5

# 【自定义:Agent 的系统提示词,例如「你是一个乐于助人的助手,可以使用提供的工具完成任务。」】
SYSTEM_PROMPT = "【系统提示词】"
```

### 4.2 大模型接口模块 llm.py

**模块职责**:【自定义说明,例如「封装与大模型的所有交互,其他模块不直接接触 HTTP 请求;更换大模型供应商时,通常只需要修改本模块与 4.1 的接口地址」】

**代码示例**:

```python
"""【模块说明:例如「封装大模型接口,Agent 只通过本模块与模型交互」】"""

import os

import requests

from config import API_BASE_URL, API_KEY_ENV, MODEL_NAME, SYSTEM_PROMPT


def chat(messages, tools):
    """【函数说明】向大模型发送一次请求(OpenAI 兼容接口格式,DeepSeek 同此格式)。

    Args:
        messages: 对话历史,格式为 [{"role": "user"/"assistant"/"tool", "content": ...}]
        tools: 工具定义列表(见 tools.py)
    Returns:
        响应 JSON(已解析为 dict);调用方通过 choices[0].finish_reason 判断下一步
    """
    resp = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get(API_KEY_ENV)}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_NAME,
            # OpenAI 兼容格式:系统提示词作为第一条 system 角色消息
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            "tools": tools,
            # 【自定义:auto=模型自行决定;也可写成强制指定某个工具名】
            "tool_choice": "auto",
            "max_tokens": 【最大输出长度,例如 1024】,
        },
        timeout=【请求超时秒数,例如 60】,
    )
    # 【自定义:失败处理,例如打印响应内容后重试或报错】
    resp.raise_for_status()
    return resp.json()
```

### 4.3 工具模块 tools.py

**模块职责**:【自定义说明,例如「定义 Agent 可用的工具(名称、说明、参数)以及每个工具的具体实现;新增工具时只需在 TOOLS 中加一条定义,并在 call_tool 中加一个分支」】

**代码示例**:

```python
"""【模块说明:例如「定义 Agent 可以调用的工具及其实现」】"""

import datetime

# 【自定义:工具定义列表。OpenAI 兼容格式:tools → function → parameters
#  描述写得越详细,模型越知道什么时候该用这个工具】
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # 【自定义:按这个格式继续添加你的工具】
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "【工具名,如 get_weather】",
    #         "description": "【工具说明:什么时候用、做什么】",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "【参数名】": {"type": "string", "description": "【参数说明】"},
    #             },
    #             "required": ["【参数名】"],
    #         },
    #     },
    # },
]


def call_tool(name, args):
    """【函数说明】根据工具名分发到具体实现,返回执行结果的字符串。

    Args:
        name: 模型请求的工具名
        args: 模型传入的参数 dict
    Returns:
        工具执行结果(字符串),会作为 tool_result 回传给模型
    """
    if name == "get_current_time":
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 【自定义:新增工具时,在这里添加对应分支,例如
    #  if name == "get_weather":
    #      return 【调用你自己的天气查询函数】(**args) 】
    raise ValueError(f"未知工具: {name}")
```

### 4.4 主程序(运行循环)agent_demo.py

**模块职责**:【自定义说明,例如「实现 Agent 的核心循环:思考 → 调用工具 → 观察结果 → 继续,直到模型给出最终回复」】

**代码示例**:

```python
"""【模块说明:例如「主程序,实现 Agent 的核心运行循环」】"""

import json

from config import MAX_TOOL_ROUNDS
from llm import chat
from tools import TOOLS, call_tool


def run_agent(user_input):
    """【函数说明】执行一轮完整的 Agent 问答。

    Args:
        user_input: 用户输入
    Returns:
        最终回复文本
    """
    # 1. 初始化对话历史(system 提示词由 llm.chat 自动加到最前面)
    messages = [{"role": "user", "content": user_input}]

    for _ in range(MAX_TOOL_ROUNDS):
        # 2. 让大模型决定:直接回复,还是调用工具
        response = chat(messages, TOOLS)

        # 3. 取本轮回复消息(可能含 tool_calls),原样加入历史
        message = response["choices"][0]["message"]
        messages.append(message)

        # 4. 模型不再请求工具 → 已得到最终回复,结束循环
        if response["choices"][0]["finish_reason"] != "tool_calls":
            break

        # 5. 逐个执行模型请求的工具
        for tool_call in message["tool_calls"]:
            name = tool_call["function"]["name"]
            # 【说明:OpenAI 兼容格式的参数是 JSON 字符串,必须先解析成 dict】
            args = json.loads(tool_call["function"]["arguments"])
            print(f"[Agent] 调用工具 {name}({args})")
            result = call_tool(name, args)

            # 6. 工具结果作为 role=tool 的消息回传,用 tool_call_id 关联
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    # 7. 提取最终文本回复
    return message["content"]


if __name__ == "__main__":
    print(run_agent(input("请输入你的问题: ")))
```

## 5. 运行流程

> 说明:与 4.4 的代码一一对应,以下每步可对照代码中的注释理解。

1. 【第一步:例如「接收用户输入」】
2. 【第二步:例如「大模型判断是否需要调用工具」】
3. 【第三步:例如「调用【工具名】并获取结果」】
4. 【第四步:例如「根据工具结果生成最终回复」】
5. 【第五步:例如「输出回复,等待下一轮输入」】
6. 【结束条件:例如「用户输入退出指令或达到轮次上限」】

## 6. 功能清单

| 功能 | 功能说明 | 优先级 |
| --- | --- | --- |
| 【功能一:如「基础问答」】 | 【说明该功能的行为】 | 【高/中/低】 |
| 【功能二:如「调用某工具」】 | 【说明该功能的行为】 | 【高/中/低】 |
| 【功能三】 | 【说明该功能的行为】 | 【高/中/低】 |

## 7. 文件结构规划

- agent_demo.py — 主程序,Agent 运行循环(见 4.4)
- llm.py — 大模型接口模块(见 4.2)
- tools.py — 工具定义与实现模块(见 4.3)
- config.py — 配置模块(见 4.1)
- 【自定义:如还需要「日志模块」「记忆模块」等,在此补充】

## 8. 环境与依赖

- Python 版本:【例如 3.10+】
- 操作系统:【例如 Windows / macOS / Linux】
- 依赖库:
  - 【依赖一:如 requests —— HTTP 客户端库,本示例直接调用大模型 HTTP 接口,不使用厂商 SDK】
  - 【依赖二:如需其他库在此补充】
- 环境变量 / 密钥:
  - 【例如「DEEPSEEK_API_KEY = 你的 API Key」,不要提交到代码仓库】
  - 【例如「更换供应商后,对应的环境变量与 SDK」】

## 9. 测试与验证

- 测试场景一:【描述一个典型输入与期望输出】
- 测试场景二:【描述工具调用成功时的表现】
- 测试场景三:【描述工具调用失败 / 模型无法处理时的表现】
- 验收标准:【什么样的结果算「示例完成」】

## 10. 已知限制与后续扩展

- 已知限制:【例如「每次运行上下文不保留」「仅支持单用户」「未做并发与超时处理」】
- 后续扩展方向:
  - 【扩展一:例如「加入长期记忆(向量数据库)」】
  - 【扩展二:例如「接入更多工具」】
  - 【扩展三:例如「支持流式输出」】

---

## 附:自定义清单(填写时可对照检查)

- [ ] 所有【】占位符已替换为自定义内容(包括代码示例中的)
- [ ] 章节结构符合你的实际需求(可增删)
- [ ] 功能清单与实际实现一致
- [ ] 运行流程与实际逻辑一致
- [ ] 代码示例与你调用大模型的方式一致(本示例为 requests 直连 OpenAI 兼容接口,未使用厂商 SDK)
