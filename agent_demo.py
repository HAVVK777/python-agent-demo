import os
import re
import requests


# 【自定义:你的 API Key 所在的环境变量名,不要把 Key 直接写在这里】
API_KEY_ENV = "ANTHROPIC_API_KEY"

# 【自定义:模型名称,例如 claude-opus-5 / claude-sonnet-5 / claude-haiku-4-5】
MODEL_NAME = "deepseek-v4-flash"

# 【自定义:单次问答中最多允许调用几次工具,防止 Agent 陷入死循环】
MAX_TOOL_ROUNDS = 5

# 【自定义:Agent 的系统提示词,例如「你是一个乐于助人的助手,可以使用提供的工具完成任务。」】
SYSTEM_PROMPT = "你好一个助手，你可以利用现有的工具进行回答问题，遇到无法利用工具得出结果的问题可以回答不知道"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "caculate",
            "description": "这是一个计算器,根据数字列表和运算符列表计算出结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "num": {"type": "array", "items": {"type": "string"}, "description": "数字列表,如 ['1', '2', '3']"},
                    "operators": {"type": "array", "items": {"type": "string"}, "description": "运算符列表,如 ['+', '*']"},
                },
                "required": ["num", "operators"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名,如 '北京'"},
                },
                "required": ["city"],
            },
        },
    },
]

def caculate(num: list[str], operators: list[str]) -> int:
    expr = num[0]
    for op, n in zip(operators, num[1:]):
        expr += op + n

    # 只允许数字、四则运算符、括号和小数点,其余一律拒绝
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
        raise ValueError(f"表达式包含不允许的字符: {expr}")
    return eval(expr)

def get_weather(city:str) -> str:
    """通过 Open-Meteo 获取指定城市的当前天气(免费,无需 API Key)。"""
    # 1. 城市名 → 经纬度(Open-Meteo 地理编码接口)
    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "zh"},
        timeout=10,
    )
    geo_resp.raise_for_status()
    results = geo_resp.json().get("results") or []
    if not results:
        return f"未找到城市「{city}」的天气信息"

    place = results[0]

    # 2. 按经纬度查询当前天气
    wx_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        },
        timeout=10,
    )
    wx_resp.raise_for_status()
    cur = wx_resp.json()["current"]

    return (
        f"{place['name']} 当前天气:"
        f"{WEATHER_TEXT.get(cur['weather_code'], '未知')},"
        f"温度 {cur['temperature_2m']}℃,"
        f"风速 {cur['wind_speed_10m']} km/h"
    )


# WMO 天气代码 → 中文描述(Open-Meteo 返回的 weather_code 含义)
WEATHER_TEXT = {
    0: "晴",
    1: "大致晴朗",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "冻雾",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "大毛毛雨",
    56: "冻毛毛雨",
    57: "强冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "阵雨",
    82: "强阵雨",
    85: "小阵雪",
    86: "强阵雪",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
}


def call_tool(name: str, args: dict) -> str:
    """工具分发:根据模型请求的工具名调用对应实现。"""
    if name == "caculate":
        return str(caculate(args["num"], args["operators"]))
    if name == "get_weather":
        return get_weather(args["city"])
    raise ValueError(f"未知工具: {name}")


from llm import chat
def run_agent(user_input:str)->str:
    messages = [{"role":"user","content":user_input}]
    