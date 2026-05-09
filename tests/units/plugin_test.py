import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_plugin_metadata(app: App):
    from nonebot_plugin_fakemsg_next import __plugin_meta__

    assert __plugin_meta__.name == "伪造消息 Next"
    assert __plugin_meta__.description == "使用显式命令触发的合并转发伪造消息插件。"
    assert __plugin_meta__.type == "application"
