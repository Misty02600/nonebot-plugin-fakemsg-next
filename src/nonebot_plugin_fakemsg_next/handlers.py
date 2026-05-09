from contextlib import suppress

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.params import CommandArg

from .config import plugin_config
from .parser import parse_quick_message


async def resolve_display_name(
    bot: Bot,
    event: GroupMessageEvent,
    user_id: int,
) -> str:
    """解析伪造节点的显示名。

    优先尝试群昵称，失败时直接使用 QQ 号字符串。

    Args:
        bot: 当前 OneBot v11 bot 实例。
        event: 触发命令的群消息事件。
        user_id: 目标用户 QQ 号。

    Returns:
        适合写入合并转发节点的显示名。
    """

    with suppress(Exception):
        info = await bot.get_group_member_info(
            group_id=event.group_id,
            user_id=user_id,
        )
        display_name = info.get("nickname")
        if display_name:
            return display_name

    return str(user_id)


fakemsg_command = on_command(
    "伪造消息",
    aliases={"fakemsg", "消息伪造"},
    priority=10,
    block=True,
)


@fakemsg_command.handle()
async def handle_fakemsg(
    bot: Bot,
    event: GroupMessageEvent,
    arg: Message = CommandArg(),
) -> None:
    try:
        parsed = parse_quick_message(
            arg,
            separator=plugin_config.fakemsg_next_quick_separator,
        )
    except ValueError as exc:
        await fakemsg_command.finish(str(exc))

    messages = [
        MessageSegment.node_custom(
            user_id=node.target_id,
            nickname=await resolve_display_name(bot, event, node.target_id),
            content=node.content,
        )
        for node in parsed
    ]
    await bot.send_group_forward_msg(group_id=event.group_id, messages=messages)
    await fakemsg_command.finish()
