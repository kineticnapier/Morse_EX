from pykakasi import kakasi
import discord
from discord import Interaction
from typing import cast

def katakana_to_hiragana(text: str) -> str:
    result = []
    for ch in text:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            result.append(chr(code - 0x60))
        else:
            result.append(ch)
    return "".join(result)

def normalize_japanese_text(text: str) -> str:
    kks = kakasi()
    converted = kks.convert(text)
    reading = "".join(item.get("kana") or item.get("orig", "") for item in converted)
    reading = katakana_to_hiragana(reading)
    reading = reading.replace("ー", "")
    return reading

def suffix_unconverted(flag: bool) -> str:
    return "\n(変換できない文字がありました)" if flag else ""

INSTALLS_KW = {"guilds": True, "users": True}
CONTEXTS_KW = {"guilds": True, "dms": True, "private_channels": True}
def allow_everywhere(func):
    func = discord.app_commands.allowed_installs(**INSTALLS_KW)(func)
    func = discord.app_commands.allowed_contexts(**CONTEXTS_KW)(func)
    return func

async def send_ephemeral(interaction: Interaction, message: str) -> None:
    await interaction.response.send_message(message, ephemeral=True)

def get_messageable_channel(
    interaction: Interaction,
) -> discord.abc.Messageable | None:
    channel = interaction.channel

    if channel is None:
        return None

    if isinstance(channel, discord.ForumChannel):
        return None

    return cast(discord.abc.Messageable, channel)

async def fetch_message_in_current_channel(
    interaction: Interaction,
    message_id: str,
) -> discord.Message | None:
    if not message_id.isdigit():
        await send_ephemeral(interaction, "メッセージIDは数字で指定してください。")
        return None

    channel = get_messageable_channel(interaction)
    if channel is None:
        await send_ephemeral(
            interaction,
            "このコマンドはメッセージを取得できるチャンネルでのみ使用できます。",
        )
        return None

    try:
        return await channel.fetch_message(int(message_id))
    except discord.NotFound:
        await send_ephemeral(
            interaction,
            "そのメッセージはこのチャンネルで見つかりませんでした。",
        )
    except discord.Forbidden:
        await send_ephemeral(
            interaction,
            "そのメッセージを読む権限がありません。",
        )
    except discord.HTTPException as e:
        await send_ephemeral(
            interaction,
            f"取得に失敗しました: {e}",
        )

    return None