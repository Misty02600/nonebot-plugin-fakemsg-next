from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="伪造消息 Next",
    description="使用显式命令触发的合并转发伪造消息插件。",
    usage="伪造消息 @用户说ping|@用户说pong",
    type="application",
    homepage="https://github.com/Misty02600/nonebot-plugin-fakemsg-next",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={"author": "Misty02600"},
)

from . import handlers as handlers
