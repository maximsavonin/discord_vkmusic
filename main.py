import discord
from discord.ext import commands
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {'format': 'bestaudio/best', 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_source(ctx, url):
    voice = ctx.voice_client

    if not voice:
        if ctx.author.voice is None:
            await ctx.send("Ты не в голосовом канале!")
            return
        channel = ctx.author.voice.channel
        voice = await channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            # Если это плейлист — берём все треки
            for entry in info['entries']:
                await ctx.send(f"Добавлен в очередь: {entry['title']}")
                await play_track(ctx, entry['url'])
        else:
            await play_track(ctx, info['url'], info['title'])

async def play_track(ctx, url, title=None):
    voice = ctx.voice_client
    if not voice.is_playing():
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        voice.play(source, after=lambda e: print(f"Ошибка: {e}") if e else None)
        await ctx.send(f"▶️ Играет: {title if title else url}")
    else:
        await ctx.send("Сейчас уже играет музыка! Останови её командой !stop")

@bot.command()
async def play(ctx, url):
    await play_source(ctx, url)

@bot.command()
async def playlist(ctx, url):
    await play_source(ctx, url)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Музыка остановлена")

bot.run(TOKEN)