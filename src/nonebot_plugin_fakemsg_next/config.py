from nonebot.plugin import get_plugin_config
from pydantic import BaseModel, Field


class Config(BaseModel):
    fakemsg_next_quick_separator: str = Field(
        default="|",
        min_length=1,
        max_length=1,
        description="多条伪造消息的分隔符，必须是单个字符。",
    )


plugin_config = get_plugin_config(Config)
