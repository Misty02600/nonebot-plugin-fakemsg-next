<div align="center">
  <img src="https://github.com/Misty02600/nonebot-plugin-template/releases/download/assets/NoneBotPlugin.png" width="310" alt="logo">

## ✨ nonebot-plugin-fakemsg-next ✨

 NoneBot 合并转发伪造消息插件。
</div>

## 介绍

[Cvandia/nonebot-plugin-fakemsg](https://github.com/Cvandia/nonebot-plugin-fakemsg) 支持图片和 QQ 表情的实现版本


## 安装

### 使用 uv

```bash
uv add nonebot-plugin-fakemsg-next
```

### 使用 nb-cli

```bash
nb plugin install nonebot-plugin-fakemsg-next --upgrade
```

在 `pyproject.toml` 中启用插件：

```toml
[tool.nonebot.plugins]
nonebot-plugin-fakemsg-next = ["nonebot_plugin_fakemsg_next"]
```

## 使用

每个分隔符分隔一条完整的伪造节点，每段均需显式写目标：

```text
/伪造消息 @user1说ping
/伪造消息 @user1说ping|@user1说pong
/消息伪造 @user1说ping|@user2说pong
/fakemsg @user1说ping|@user2说pong
```

- 每条消息结构必须为 `@用户说<内容>`
- 仅支持群聊中通过 `@用户` 指定伪造目标
- 如果正文需要字面量 `|`，可写成 `\|`

## 配置


```env
FAKEMSG_NEXT_QUICK_SEPARATOR=|
```

- `fakemsg_next_quick_separator`
  - 单字符分隔符，默认 `|`
