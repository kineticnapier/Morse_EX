import os
from typing import cast

import discord
from discord import Client, Intents, Interaction, app_commands
from discord.app_commands import CommandTree
from dotenv import load_dotenv

from conv_func import morse_to_text, text_to_morse
from helper_func import suffix_unconverted, allow_everywhere, send_ephemeral, fetch_message_in_current_channel


class MyClient(Client):
    def __init__(self, intents: Intents) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self) -> None:
        if self.user is not None:
            print(f"login: {self.user.name} [{self.user.id}]")


intents = Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# ----------------------
# スラッシュコマンド
# ----------------------
@client.tree.command(name="encrypt", description="平文をモールス信号に変換します")
@allow_everywhere
@app_commands.describe(
    text="変換したい平文",
    mode="jp / en",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="jp", value="jp"),
    app_commands.Choice(name="en", value="en"),
])
async def encrypt(
    interaction: Interaction,
    text: str,
    mode: app_commands.Choice[str],
) -> None:
    morse, flag = text_to_morse(text, mode.value)
    await interaction.response.send_message(morse + suffix_unconverted(flag))


@client.tree.command(name="decrypt", description="指定したメッセージIDのモールス本文を平文に戻す")
@allow_everywhere
@app_commands.describe(
    id="現在のチャンネル内のメッセージID",
    mode="jp / en",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="jp", value="jp"),
    app_commands.Choice(name="en", value="en"),
])
async def decrypt(
    interaction: Interaction,
    id: str,
    mode: app_commands.Choice[str],
) -> None:
    message = await fetch_message_in_current_channel(interaction, id)
    if message is None:
        return

    content = message.content.strip()
    if not content:
        await send_ephemeral(interaction, "本文が空です。")
        return

    plain, flag = morse_to_text(content, mode.value)
    await interaction.response.send_message(
        f"モールス:\n{content}\n\n平文:\n{plain}{suffix_unconverted(flag)}"
    )


@client.tree.command(name="decrypt_text", description="モールス信号を直接平文に戻す")
@allow_everywhere
@app_commands.describe(
    text="モールス信号",
    mode="jp / en",
)
@app_commands.choices(mode=[
    app_commands.Choice(name="jp", value="jp"),
    app_commands.Choice(name="en", value="en"),
])
async def decrypt_text(
    interaction: Interaction,
    text: str,
    mode: app_commands.Choice[str],
) -> None:
    plain, flag = morse_to_text(text, mode.value)
    await interaction.response.send_message(plain + suffix_unconverted(flag))


# ----------------------
# コンテキストメニュー
# ----------------------
@client.tree.context_menu(name="Encrypt to Morse")
@allow_everywhere
async def encrypt_message(interaction: Interaction, message: discord.Message) -> None:
    content = message.content.strip()
    if not content:
        await send_ephemeral(interaction, "本文が空です。")
        return

    # text_to_morse が auto 非対応なら jp/en を明示する必要あり
    morse, flag = text_to_morse(content, "jp")
    await interaction.response.send_message(morse + suffix_unconverted(flag))


@client.tree.context_menu(name="Decrypt Morse")
@allow_everywhere
async def decrypt_message(interaction: Interaction, message: discord.Message) -> None:
    content = message.content.strip()
    if not content:
        await send_ephemeral(interaction, "本文が空です。")
        return

    # morse_to_text が auto 非対応なら jp/en を明示する必要あり
    plain, flag = morse_to_text(content, "jp")
    await interaction.response.send_message(
        f"モールス:\n{content}\n\n平文:\n{plain}{suffix_unconverted(flag)}"
    )


def main() -> None:
    load_dotenv()
    token = os.getenv("TOKEN")

    if not token:
        raise RuntimeError("TOKEN が設定されていません。")

    client.run(token)


if __name__ == "__main__":
    main()