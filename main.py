import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()

client = commands.Bot(command_prefix='`')

status = ['Bagallah', 'Ji ki', 'Jai']
queue = []
loop = False

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')



@client.command(name='bolo', help='This command returns the latency with Jai Shri Ram')
async def bolo(ctx):
    await ctx.send(f'**Shri Ram Ji Ki Jai** {round(client.latency * 1000)}x')

@client.command(name='bagallah', help='This command returns a random welcome message')
async def bagallah(ctx):
    responses = ['Bagallah', 'https://cdn.discordapp.com/attachments/700660206329135196/832853494502260746/video0-66.mp4', 'Bagai Gau', ' :swagpray:', 'Arpit Gau']
    await ctx.send(choice(responses))


@client.command(name='Bani hum nahaile', help='Bani hum nahaile aaj semphul se')
async def Bani_hum_nahaile(ctx):
  await ctx.send("https://www.youtube.com/watch?v=MsYRH5bCA2U")

@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    
@client.command(name='disconect', help='This command stops the music and makes the bot leave the voice channel')
async def disconnect(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()



@client.command(name='loop', help='This command toggles loop mode')
async def loop_(ctx):
    global loop

    if loop:
        await ctx.send('Loop mode is now `False!`')
        loop = False
    
    else: 
        await ctx.send('Loop mode is now `True!`')
        loop = True

@client.command(name='play', help='This command plays music')
async def play(ctx):
    global queue

    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    try: await channel.connect()
    except: pass

    server = ctx.message.guild
    voice_channel = server.voice_client
    
    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            
            if loop:
                queue.append(queue[0])

            del(queue[0])
            
        await ctx.send('**Now playing:** {}'.format(player.title))

    except:
        await ctx.send('Nothing in your queue! Use `queue` to add a song!')



@client.command()
async def pause(ctx):
  await ctx.voice_client.pause()
  await ctx.send("Playback Paused")

@client.command()
async def resume(ctx):
  await ctx.voice_client.resume()
  await ctx.send("Playback Resumed")

@client.command()
async def stop(ctx):
  await ctx.voice_client.stop()
  await ctx.send("Playback Resumed")



@client.command(name='queue')
async def queue_(ctx, url):
    global queue
    
    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

@client.command(name='remove')
async def remove(ctx, number):
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')
    
    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')

@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')

@tasks.loop(seconds=2)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run('OTIwNTYxOTgxMzc3OTAwNTc1.YbmKJw.AtO8GDFZx7f62eFcYuPYgwbNILc')