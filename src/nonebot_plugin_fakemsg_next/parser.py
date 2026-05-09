from typing import NamedTuple

from nonebot.adapters.onebot.v11 import Message, MessageSegment


class ParsedNode(NamedTuple):
    target_id: int
    content: Message


def _trim_message_edges(message: Message) -> Message:
    segments = list(message)
    while segments and segments[0].type == "text":
        stripped = segments[0].data.get("text", "").lstrip()
        if not stripped:
            segments.pop(0)
            continue
        if stripped != segments[0].data.get("text", ""):
            segments[0] = MessageSegment.text(stripped)
        break

    while segments and segments[-1].type == "text":
        stripped = segments[-1].data.get("text", "").rstrip()
        if not stripped:
            segments.pop()
            continue
        if stripped != segments[-1].data.get("text", ""):
            segments[-1] = MessageSegment.text(stripped)
        break

    return Message(segments)


def _format_error(index: int, reason: str) -> ValueError:
    return ValueError(f"格式不正确：第{index}条消息{reason}")


def split_message_chunks(message: Message, *, separator: str) -> list[Message]:
    """把一条命令参数拆成多条伪造消息。

    只有文本段里的分隔符会触发拆分，图片、表情、at 等非文本段会留在
    当前消息里。正文里需要保留分隔符本身时，可以在它前面加反斜杠转义。
    连续分隔符、开头分隔符和结尾分隔符会产生空消息片段，交给后续格式
    校验返回精确错误。

    Args:
        message: 待拆分的原始消息。
        separator: 已从配置读取并校验过的单字符分隔符。

    Returns:
        按顺序拆出的消息片段列表。
    """

    chunks: list[Message] = []
    current = Message()

    def append_text(text: str) -> None:
        nonlocal current
        if text:
            current += MessageSegment.text(text)

    def flush_chunk() -> None:
        nonlocal current
        chunk = _trim_message_edges(current)
        current = Message()
        chunks.append(chunk)

    for segment in _trim_message_edges(message):
        if segment.type != "text":
            current += segment
            continue

        text = segment.data.get("text", "")
        buffer: list[str] = []
        index = 0
        while index < len(text):
            char = text[index]
            if char == "\\" and index + 1 < len(text) and text[index + 1] == separator:
                buffer.append(separator)
                index += 2
                continue

            if char == separator:
                append_text("".join(buffer))
                buffer.clear()
                flush_chunk()
                index += 1
                continue

            buffer.append(char)
            index += 1

        append_text("".join(buffer))

    flush_chunk()
    return chunks


def parse_targeted_message(message: Message, *, index: int = 1) -> ParsedNode:
    """解析单条“@用户说<内容>”结构。

    Args:
        message: 单条伪造消息片段。
        index: 当前片段序号，用于错误提示。

    Returns:
        解析后的目标用户和消息内容。

    Raises:
        ValueError: 当缺少用户、缺少“说”或缺少内容时抛出。
    """

    remaining = _trim_message_edges(message)
    if not remaining:
        raise _format_error(index, "缺少内容")

    first = remaining[0]
    if first.type != "at":
        raise _format_error(index, "缺少用户")

    qq = first.data.get("qq")
    if not qq or qq == "all":
        raise _format_error(index, "缺少用户")
    target_id = int(qq)
    payload = _trim_message_edges(remaining[1:])
    if not payload or payload[0].type != "text":
        raise _format_error(index, "缺少“说”")

    first_text = payload[0].data.get("text", "")
    if not first_text.startswith("说"):
        raise _format_error(index, "缺少“说”")

    rest = first_text[1:]
    if rest:
        payload = MessageSegment.text(rest) + payload[1:]
    else:
        payload = payload[1:]

    content = _trim_message_edges(payload)
    if not content:
        raise _format_error(index, "缺少内容")

    return ParsedNode(target_id=target_id, content=content)


def parse_quick_message(
    message: Message,
    *,
    separator: str,
) -> list[ParsedNode]:
    """解析整条快捷命令参数。

    Args:
        message: 命令参数部分的原始消息。
        separator: 多条伪造消息的顶层分隔符。

    Returns:
        每个分段对应的一组目标用户和消息内容。

    Raises:
        ValueError: 当任意分段不符合“@用户说<内容>”结构时抛出。
    """

    chunks = split_message_chunks(message, separator=separator)
    return [
        parse_targeted_message(chunk, index=index)
        for index, chunk in enumerate(chunks, start=1)
    ]
