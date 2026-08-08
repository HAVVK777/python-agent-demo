import json
from protocol import ToolSchema
import requests
_tool_registry:dict[str, callable] = {}


def register(name:str, description:str, parameters:dict):
    def decorator(fn: callable)->callable:
        _tool_registry[name] = fn
        fn._schema = ToolSchema(name=name,description=description,parameters=parameters)
        return fn
    return decorator

def get_all_schemas() -> list[ToolSchema]:
    return [fn._schema for fn in _tool_registry.values()]

def run(name: str, arguments: dict) -> str:
    fn = _tool_registry.get(name)
    if not fn:
        return json.dumps({"error": f"工具 '{name}' 不存在"}, ensure_ascii=False)
    try:
        result = fn(**arguments)
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@register(
    name="get_weather",
    description="查询指定城市的当前天气",
    parameters={
        "type":"object",
        "properties":{
            "city":{"type":"string","description":"城市名称"}
        },
        "required": ["city"],
    }
)
def get_weather(city:str):
    """这是一个天气查询方法，需要字符串形式的城市参数"""

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh"
    geo_data = requests.get(geo_url, timeout=10).json()
    if not geo_data.get("results"):
        return {"error": f"未找到城市：{city}"}

    loc = geo_data["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    name = loc.get("name", city)

    # 再查天气
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Asia/Shanghai&forecast_days=1"
    )
    weather_data = requests.get(weather_url, timeout=10).json()

    return {
        "city": name,
        "temperature": weather_data["current"]["temperature_2m"],
        "humidity": weather_data["current"]["relative_humidity_2m"],
        "wind_speed": weather_data["current"]["wind_speed_10m"],
    }