import pytest
from nonebot.adapters.onebot.v11 import Message, MessageSegment


@pytest.fixture(scope="module")
def parser_module():
    from nonebot_plugin_fakemsg_next import parser

    return parser


def test_parse_targeted_message_with_at_target(parser_module):
    message = Message(
        [
            MessageSegment.at(123456),
            MessageSegment.text("说ping"),
            MessageSegment.image("https://example.com/a.png"),
        ]
    )

    parsed = parser_module.parse_targeted_message(message)

    assert parsed.target_id == 123456
    assert [segment.type for segment in parsed.content] == ["text", "image"]


def test_split_message_chunks_preserves_rich_segments(parser_module):
    message = Message(
        [
            MessageSegment.at(123456),
            MessageSegment.text("说ping|"),
            MessageSegment.at(123456),
            MessageSegment.text("说"),
            MessageSegment.image("https://example.com/a.png"),
        ]
    )

    chunks = parser_module.split_message_chunks(message, separator="|")

    assert len(chunks) == 2
    assert [segment.type for segment in chunks[0]] == ["at", "text"]
    assert [segment.type for segment in chunks[1]] == ["at", "text", "image"]


def test_split_message_chunks_supports_escaped_separator(parser_module):
    chunks = parser_module.split_message_chunks(
        Message(r"ping\|payload|pong"),
        separator="|",
    )

    assert len(chunks) == 2
    assert str(chunks[0]) == "ping|payload"


def test_parse_quick_message_supports_multiple_complete_nodes(parser_module):
    parsed = parser_module.parse_quick_message(
        Message(
            [
                MessageSegment.at(123456),
                MessageSegment.text("说ping|"),
                MessageSegment.at(12345678),
                MessageSegment.text("说pong"),
            ]
        ),
        separator="|",
    )

    assert [item.target_id for item in parsed] == [123456, 12345678]
    assert str(parsed[0].content) == "ping"
    assert str(parsed[1].content) == "pong"


def test_parse_quick_message_missing_user(parser_module):
    with pytest.raises(ValueError, match="格式不正确：第1条消息缺少用户") as exc:
        parser_module.parse_quick_message(Message("说ping"), separator="|")

    assert str(exc.value) == "格式不正确：第1条消息缺少用户"


def test_parse_quick_message_rejects_text_target(parser_module):
    with pytest.raises(ValueError, match="格式不正确：第1条消息缺少用户") as exc:
        parser_module.parse_quick_message(Message("123456ping"), separator="|")

    assert str(exc.value) == "格式不正确：第1条消息缺少用户"


def test_parse_quick_message_missing_say(parser_module):
    with pytest.raises(ValueError, match="格式不正确：第1条消息缺少“说”") as exc:
        parser_module.parse_quick_message(
            MessageSegment.at(123456) + Message("ping"),
            separator="|",
        )

    assert str(exc.value) == "格式不正确：第1条消息缺少“说”"


def test_parse_quick_message_missing_content(parser_module):
    with pytest.raises(ValueError, match="格式不正确：第1条消息缺少内容") as exc:
        parser_module.parse_quick_message(
            MessageSegment.at(123456) + MessageSegment.text("说"),
            separator="|",
        )

    assert str(exc.value) == "格式不正确：第1条消息缺少内容"


def test_parse_quick_message_reports_empty_chunk(parser_module):
    with pytest.raises(ValueError, match="格式不正确：第2条消息缺少内容") as exc:
        parser_module.parse_quick_message(
            MessageSegment.at(123456) + Message("说ping||") + MessageSegment.at(123456),
            separator="|",
        )

    assert str(exc.value) == "格式不正确：第2条消息缺少内容"
