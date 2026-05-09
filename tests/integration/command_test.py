import pytest
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message, MessageSegment
from nonebug import App
from tests.units.fake import fake_group_message_event_v11


@pytest.mark.asyncio
async def test_command_syntax_event_flow(app: App):
    from nonebot_plugin_fakemsg_next.handlers import fakemsg_command

    message = Message(
        [
            MessageSegment.text("/伪造消息 "),
            MessageSegment.at(123456),
            MessageSegment.text("说ping"),
            MessageSegment.face(66),
            MessageSegment.text("|"),
            MessageSegment.at(12345678),
            MessageSegment.text("说pong"),
            MessageSegment.image("https://example.com/a.png"),
        ]
    )
    event = fake_group_message_event_v11(message=message, raw_message=str(message))

    expected_messages = [
        MessageSegment.node_custom(
            user_id=123456,
            nickname="Alice",
            content=MessageSegment.text("ping") + MessageSegment.face(66),
        ),
        MessageSegment.node_custom(
            user_id=12345678,
            nickname="Bob",
            content=MessageSegment.text("pong")
            + MessageSegment.image("https://example.com/a.png"),
        ),
    ]

    async with app.test_matcher(fakemsg_command) as ctx:
        adapter = ctx.create_adapter(base=Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter, self_id="1")

        ctx.receive_event(bot, event)
        ctx.should_finished(fakemsg_command)
        ctx.should_call_api(
            "get_group_member_info",
            {"group_id": event.group_id, "user_id": 123456},
            result={"card": "不使用的群名片", "nickname": "Alice"},
        )
        ctx.should_call_api(
            "get_group_member_info",
            {"group_id": event.group_id, "user_id": 12345678},
            result={"card": "不使用的群名片", "nickname": "Bob"},
        )
        ctx.should_call_api(
            "send_group_forward_msg",
            {"group_id": event.group_id, "messages": expected_messages},
            result={"message_id": 1},
        )


@pytest.mark.asyncio
async def test_invalid_format_replies_precise_reason(app: App):
    from nonebot_plugin_fakemsg_next.handlers import fakemsg_command

    message = Message("/消息伪造 123456ping")
    event = fake_group_message_event_v11(message=message, raw_message=str(message))

    async with app.test_matcher(fakemsg_command) as ctx:
        adapter = ctx.create_adapter(base=Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter, self_id="1")

        ctx.receive_event(bot, event)
        ctx.should_finished(fakemsg_command)
        ctx.should_call_send(
            event,
            "格式不正确：第1条消息缺少用户",
            bot=bot,
        )
