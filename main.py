import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import vk_api

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
VK_TOKEN = os.getenv("VK_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # чтобы бот видел команды в чатах
intents.voice_states = True     # чтобы бот видел, кто в голосовом канале

bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {'format': 'bestaudio/best', 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Подключился к {channel.name}")
    else:
        await ctx.send("Вы не в голосовом канале!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Отключился от голосового канала")
    else:
        await ctx.send("Я не в голосовом канале!")

async def play_vk_track(ctx, vk_url):
    voice = ctx.voice_client
    if not voice:
        if not ctx.author.voice:
            await ctx.send("Ты не в голосовом канале!")
            return
        channel = ctx.author.voice.channel
        voice = await channel.connect()

    # Получаем прямую ссылку на аудио через VK API
    try:
        audio_list = vk.audio.search(q=vk_url, count=1)
        if not audio_list['items']:
            await ctx.send("Не удалось найти трек в VK")
            return
        audio = audio_list['items'][0]
        audio_url = audio['url']
        title = audio['artist'] + " - " + audio['title']
    except Exception as e:
        await ctx.send(f"Ошибка при получении трека из VK: {e}")
        return

    # Проигрываем через FFmpeg
    if not voice.is_playing():
        source = await discord.FFmpegOpusAudio.from_probe(audio_url, **FFMPEG_OPTIONS)
        voice.play(source, after=lambda e: print(f"Ошибка: {e}") if e else None)
        await ctx.send(f"▶️ Играет: {title}")
    else:
        await ctx.send("Сейчас уже играет музыка! Останови её командой !stop")

@bot.command()
async def play(ctx, vk_query):
    await play_vk_track(ctx, vk_query)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Музыка остановлена")

bot.run(TOKEN)