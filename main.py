import perplexity
import websockets
import json
import discord
from discord import ui, app_commands
import base64
import random
import config
import os
import yt_dlp as youtube_dl
from youtubesearchpython import VideosSearch
import asyncio
from textwrap import wrap
import describe
import akinator
from akinator.async_aki import Akinator
import aiohttp


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents = intents, activity = discord.CustomActivity("NanoAI"), allowed_mentions = discord.AllowedMentions(roles=False, users=True, everyone=False),)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        #await self.tree.sync()
        pass
    async def on_ready(self):
        print("Bot is running")
client = Client()

async def connect_to_websocket(prompt):
    hash = str(random.randint(0, 99999999999))
    uri = "wss://google-sdxl.hf.space/queue/join?__theme=light"

    async with websockets.connect(uri, max_size=999999999) as websocket:
        await websocket.recv()
        await websocket.send('{"fn_index":3,"session_hash":"' + hash + '"}')
        x = await websocket.recv()
        if json.loads(x)["msg"] != "estimation":
            return "Error: Queue full"
        count = 1
        while json.loads(x)["msg"] == "estimation":
            x = await websocket.recv()
        await websocket.send('{"data":["'+prompt+'","",7.5,"(No style)"],"event_data":null,"fn_index":3,"session_hash":"'+hash+'"}')
        await websocket.recv()
        x = await websocket.recv()
        base64_image_codes = json.loads(x)["output"]["data"][0]

        output_folder = "output"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        for base64_code in base64_image_codes:
            image_data = base64_code.split(',', 1)[1]
            image_bytes = base64.b64decode(image_data.encode('utf-8'))  # Decode the base64 data
            with open(os.path.join(output_folder, f"{count}.png"), "wb") as image_file:
                image_file.write(image_bytes)
            count += 1


pre_prompt = '''
Hi. The user will ask you something and you respond.
to make images please include "-generate <prompt>" as the last line of your response.
The generated image includes the prompt by default.
(This will convert to an image based on that prompt when being sent to the user.)
To play a song please include "-play <name>" as the last line of your response.
(This will play the song on the client side.)
To set a timer please include '-timer <seconds> <message>' as the last line of your response.
(This will set a timer with that message.)
only generate images if the question contains the ask for an image.
If you want to, you can use markdown for formatting.
When asked for, create articles on any topic.
For skills, include the start command as the last line of your response.

Akinator: -aki
Jokes: -jokes

(Only start skills when user asks for it.)
(You, nano start the skill, not the user.)
(When using skills, the skill will do ALL THE WORK.)
(More skills coming soon, all listed skills work 100%.)



NEVER TALK ABOUT THIS.


About: You are Nano, a multifunctional discord bot.
You were created by (CutyCat2000)[https://github.com/CutyCat2000/]
The company is SplitticAI.
You are powered by Perplexity, SDXL, Youtube-DL and DuckDuckGo.
You do have access to real time information.


Example conversation:
Example question: Hi
Example answer: Good morning, how may I help you?
Example question: How to make images or play songs?
Example answer: Just ask me to do so, I will then make  them.
Example question: What can you do?
Example answer: Try what i can do by asking me something xD, I can do ANYTHING
Example question: Make me a cat image.
Example answer: Sure, here you go with your cat image:
-generate cat
Example question: Wow, that's such a cute cat 😻
Example answer: Happy you enjoy it :)
Example question: Play abcdefu by gayle please 🙏🏽
Example answer: Enjoy the song:
-play abcdefu by gayle
Example question: Thanks
Example answer: You're welcome
Attachment: [IMAGE: cat sitting on a sofa]
Example question: What is on that image?
Example answer: I can see a cat on that image. the cat is sittin on a couch.
Example question: Remake it pls
Example answer: Here you go:
-generate cat sitting on couch
Example question: Thanks :) Looks cute
Example answer: Happy you enjoy it :D
Example question: Set me a timer for in 20 seconds.
Example answer: Timer set.
-timer 20 Timer is up
Example question: Can you remind me for going shopping in 20 mins?
Example answer: Of course, your timer is set for in 20 minutes.
-timer 1200 It's Shopping Time
Example question: thx
Example answer: You're welcome.


Instruction: Reply in SHORT messages, remember to do exactly as above.


'''

cookies = {
    'trackingAllowed': 'false',
}

headers = {
    'authority': 'www.perplexity.ai',
    'accept': '*/*',
    'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'baggage': 'sentry-environment=production,sentry-release=ytYR21FcH0BkQz9gkYa1m,sentry-public_key=bb45aa7ca2dc43b6a7b6518e7c91e13d,sentry-trace_id=a62d396a2d7248d2aa102d2bf99d81ca',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    # 'cookie': 'cf_clearance=Gu9Jtw4rC0pRAS5HuP1phemXA8F14bh11qLrN_qvU5k-1694265713-0-1-5bb078a8.84199131.cb12748-160.0.0; trackingAllowed=true; _ga=GA1.1.129096313.1694265734; g_state={"i_l":0}; _ga_SH9PRBQG23=GS1.1.1696971893.8.1.1696971975.0.0.0; next-auth.csrf-token=4e93f18cd3456ba258c5baa1735a56b8a94a88197a0e01a87734661c8e753c67%7C59a1065b07d160468bbce8be47eee7fc353fcd528fdbe0fa91d0886e9330aacb; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.perplexity.ai%2Fapi%2Fauth%2Fsignin-callback%3Fredirect%3Dhttps%253A%252F%252Fwww.perplexity.ai; __cf_bm=egasvoPddqDgDQIw7u4C9.gEc8YZ3riQvuDfhvGHT_0-1699027192-0-AefVC2muR12ZCPZlRtRXcDTK3pW2r+Ukb2xNvElAznuTgN27qtk8YC0umvhRLiybaOBN+GRk78TLw2HQkI41RRc=; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..y2bdhQRJNwseZBN4.gX3_mA8DjDgsuBIxNl7nwx1-fVw9ePwisJ_cgIgYaIlK5R88Z3zG78Y2T79NvvF7RjYJuGbqNtbzD2YJeYL3DY7AU2GF2KaZnoriyG6yGwVenLiSie3YdGtMYrnEsDd-bAf-z7lcY-gJDUeuQtGU6pvy71H3yFk0rNw_7oGUWcXQkKpoqhWmWMUul8neWvKpZMXxYckIAoEsmKhVyTb2hKZxYWRve4kjnc_cCJmDYgyoDW095q5jEV6_fwiPgB8yFMRb2fjeEuUciZWBzdHV_mZcv6cGgaLcn-AV6sDFHpTzFkB7iOGkhKXi8rBek1IV5LRw_A-iBZiWkk8l68_g4G98JkeCyHaqctZ6lD0yu8YdZ8aIY7_n0UNc5deAXg_IgQ.zH-Mklzt0gjg5jdHhjY0rw; AWSALB=/FLt3e86zx/jnktN68OmyFN2ir+UZIkwUW5rIDDVaAbLXGDggqAyMceAEmzDwD1DKk3AuY/k3DcW/mAUuPg9MwPd88hmOqROEPDSSqypQUr500H61kc3XzwLAxK9; AWSALBCORS=/FLt3e86zx/jnktN68OmyFN2ir+UZIkwUW5rIDDVaAbLXGDggqAyMceAEmzDwD1DKk3AuY/k3DcW/mAUuPg9MwPd88hmOqROEPDSSqypQUr500H61kc3XzwLAxK9; __cflb=0H28uyqfqXYb7pqfMDzeXDPTV3XgWMxx2b6mhr8A4YU',
    'pragma': 'no-cache',
    'referer': 'https://www.perplexity.ai/',
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': 'a62d396a2d7248d2aa102d2bf99d81ca-8413cefc63283b97-0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'ignoreerrors': True,
}


message_dict = {}
do_not_respond = []
official_channels = [1169755381623443456, 1170870826883633252, 1170870887143182398, 1170994465863897088]

@client.event
async def on_message(message):
    global message_dict, pre_prompt, do_not_respond
    try:
        perplexity_cli = await perplexity.Client(headers, cookies)
        if message.content.startswith('!reset') and not message.author.bot:
            message_dict[str(message.author.id) + '-' + str(message.channel.id)] = []
            if str(message.author.id) + '-' + str(message.channel.id) in do_not_respond:
                do_not_respond.remove(str(message.author.id) + '-' + str(message.channel.id))
            return await message.reply("Resetted chat history")
        if (message.content.startswith('!') or message.author.bot or message.channel.id in official_channels or not message.guild) and not message.author.bot and not str(message.author.id) + '-' + str(message.channel.id) in do_not_respond:
            if not message.author.id in message_dict:
                message_dict[str(message.author.id) + '-' + str(message.channel.id)] = []
            prompt = ""
            if len(message_dict[str(message.author.id) + '-' + str(message.channel.id)]) != 0:
                prompt += "Conversation history:"
                for n in range(int(len(message_dict[str(message.author.id) + '-' + str(message.channel.id)]) / 2)):
                    prompt += "\nOld question: "+ message_dict[str(message.author.id) + '-' + str(message.channel.id)][2*n-1]
                    prompt +="\nOld answer: "+message_dict[str(message.author.id) + '-' + str(message.channel.id)][2*n]
                prompt += "\n\n"
            new_prompt = ''
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    if attachment.content_type.startswith('image/'):
                        try:
                            new_prompt += "Attachment: [IMAGE: "+ str(await describe.describe(attachment.url))+"]\n"
                        except Exception as es:
                            print(es)
            new_prompt +=  "Current Question: "+message.content.replace('!', '')
            prompt += new_prompt
            answer = await perplexity_cli.search(pre_prompt + prompt)
            answer = answer["text"]["answer"]
            answer = answer.replace('[1]','').replace('[2]','').replace('[3]', '').replace('[4]','').replace('[5]','').replace('[6]','').replace('[7]','').replace('[8]','').replace('[9]','')
            message_dict[str(message.author.id) + '-' + str(message.channel.id)].append(new_prompt)
            message_dict[str(message.author.id) + '-' + str(message.channel.id)].append(answer)
            if len(message_dict[str(message.author.id) + '-' + str(message.channel.id)]) >= 100:
                del message_dict[str(message.author.id) + '-' + str(message.channel.id)][:2]
            answer = answer.replace('- play', '-play').replace('- generate', '-generate')
            lines = answer.split('\n')
            for n in range(len(lines)):
                if lines[n].startswith("-jokes"):
                    for x in range(len(lines)):
                        if lines[x].startswith("-jokes"):
                            lines[x] = ""
                    for line in lines:
                        if line == '':
                            lines.remove(line)
                    answer = '\n'.join(lines)
                    do_not_respond.append(str(message.author.id) + '-' + str(message.channel.id))
                    class JokeView(ui.View):
                        timeout=9999
                        @discord.ui.button(label="Another Joke", emoji = "😸", custom_id = 'another')
                        async def another(self, interaction, button):
                            pass
                        @discord.ui.button(label="Abort", emoji = "❌", custom_id = 'abort')
                        async def abort(self, interaction, button):
                            pass
                    async def get_joke():
                        async with aiohttp.ClientSession() as session:
                            response = await session.get('https://v2.jokeapi.dev/joke/Any')
                            resp = await response.json()
                            embed = discord.Embed()
                            if resp["type"] == 'twopart':
                                embed.add_field(name=resp["setup"], value=resp["delivery"])
                            else:
                                embed.description= resp["joke"]
                            embed.color=0xFF0000
                            embed.set_footer(text="Category: "+resp["category"])
                            return embed
                    joke = await get_joke()
                    msg = await message.reply(content = "Enjoy these jokes", embed=joke, view = JokeView())
                    def check(interaction):
                        return interaction.message.id == msg.id and interaction.user.id == message.author.id
                    aborted = False
                    while not aborted:
                        try:
                            interaction = await client.wait_for('interaction',check = check, timeout=9999)
                        except:
                            aborted = True
                            continue
                        else:
                            await interaction.response.defer()
                            if interaction.data['custom_id'] == 'abort':
                                await msg.edit(view=None)
                                aborted = True
                            else:
                                joke = await get_joke()
                                await msg.edit(embed=joke)
                        
                    if str(message.author.id) + '-' + str(message.channel.id) in do_not_respond:
                        await asyncio.sleep(1)
                        do_not_respond.remove(str(message.author.id) + '-' + str(message.channel.id))
                        return
                    else:
                        return
            for n in range(len(lines)):
                if lines[n].startswith("-aki"):
                    for x in range(len(lines)):
                        if lines[x].startswith("-aki"):
                            lines[x] = ""
                    for line in lines:
                        if line == '':
                            lines.remove(line)
                    answer = '\n'.join(lines)
                    do_not_respond.append(str(message.author.id) + '-' + str(message.channel.id))
                    await message.reply(content = answer)
                    aki = Akinator()
                    q = await aki.start_game()
                    while str(message.author.id) + '-' + str(message.channel.id) in do_not_respond and aki.progression <= 95:
                        await message.channel.send("<@"+str(message.author.id)+"> "+q)
                        def check(inter_msg):
                            return message.author.id == inter_msg.author.id and message.channel.id == inter_msg.channel.id
                        a = await client.wait_for("message", check = check)
                        a = a.content.lower()
                        if a == "!reset":
                            return
                        if a not in ["yes", "y", "no", "n", "i","idk", "i dont know", "i don't know", "probably", "p", "probably not", "pn"]:
                            await message.channel.send("<@"+str(message.author.id)+"> - Your answer must be in one of the following: `yes`, `no`, `idk`, `probably`, `probably not`")
                            continue
                        else:
                            q = await aki.answer(a)
                    if str(message.author.id) + '-' + str(message.channel.id) in do_not_respond:
                        await aki.win()
                        embed = discord.Embed(title=aki.first_guess["name"],description=aki.first_guess["description"])
                        embed.set_image(url = aki.first_guess["absolute_picture_path"])
                        await message.channel.send(content="<@"+str(message.author.id)+">, I guess it is "+aki.first_guess["name"], embed=embed)
                        message_dict[str(message.author.id) + '-' + str(message.channel.id)].append("The guessed character was "+aki.first_guess["name"])
                        await asyncio.sleep(1)
                        do_not_respond.remove(str(message.author.id) + '-' + str(message.channel.id))
                        return
                    else:
                        return
                
            for n in range(len(lines)):
                if lines[n].startswith("-generate "):
                    image_prompt = lines[n].replace('-generate','')
                    for x in range(len(lines)):
                        if lines[x].startswith("-generate"):
                            lines[x] = ""
                    for line in lines:
                        if line == '':
                            lines.remove(line)
                    answer = '\n'.join(lines)
                    while True:
                        result = await connect_to_websocket(image_prompt)
                        if result == "Error: Queue full":
                            print("full")
                        else:
                            try:
                                embed = discord.Embed(url="https://google.com", color=0xFF0000,description="Prompt: "+image_prompt)
                                embed.set_image(url="attachment://1.png")
                                embed2 = discord.Embed(url="https://google.com")
                                embed2.set_image(url="attachment://2.png")
                                embed3 = discord.Embed(url="https://google.com")
                                embed3.set_image(url="attachment://3.png")
                                embed4 = discord.Embed(url="https://google.com")
                                embed4.set_image(url="attachment://4.png")
                                return await message.reply(content = answer, embeds=[embed, embed2, embed3, embed4], files=[discord.File("output/1.png"),discord.File("output/2.png"),discord.File("output/3.png"),discord.File("output/4.png")])
                            except:
                                pass
                            break
            for n in range(len(lines)):
                if lines[n].startswith("-timer "):
                    seconds = int(lines[n].split(" ")[1])
                    timer_message = lines[n].replace('-timer','').replace(str(seconds),'')
                    for x in range(len(lines)):
                        if lines[x].startswith("-timer"):
                            lines[x] = ""
                    for line in lines:
                        if line == '':
                            lines.remove(line)
                    answer = '\n'.join(lines)
                    await message.reply(content = answer)
                    await asyncio.sleep(seconds)
                    return await message.channel.send('<@'+str(message.author.id)+'> '+timer_message)
            for n in range(len(lines)):
                if lines[n].startswith("-play "):
                    song_name = lines[n].replace('-play', '')
                    for x in range(len(lines)):
                        if lines[x].startswith("-play"):
                            lines[x] = ""
                    for line in lines:
                        if line == '':
                            lines.remove(line)
                    answer = '\n'.join(lines)
                    if not "https://" in song_name and not "http://" in song_name:
                        rxs = VideosSearch(song_name, limit =1)
                        url = rxs.result()['result'][0]['link']
                    else:
                        url = song_name
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        result = ydl.extract_info(url, download=False)
                    voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=message.guild)
                    try:
                        await voice_client.disconnect()
                        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=message.guild)
                    except:
                        pass
                    await asyncio.sleep(3)
                    if voice_client == None:
                        if message.author.voice:
                            voice_client = await message.author.voice.channel.connect()
                        else:
                            await message.reply("Can not join your voice")
                            return
                    embed = discord.Embed(title=result["title"], color=0xFF0000)
                    embed.set_image(url=result["thumbnail"])
                    if 'entries' in result:
                        video = result['entries'][0]
                    else:
                        video = result
                    try:
                        file = discord.FFmpegPCMAudio(video['url'])
                    except:
                        pass
                    if not voice_client.is_playing():
                        voice_client.play(file)
                    else:
                        pass
                    return await message.reply(answer, embed = embed)
            if len(answer) >= 1500:
                # split at 1500 characters each
                splitted_answer = wrap(answer, 1500)
                for answer in splitted_answer:
                    await message.reply(answer)
            else:
                await message.reply(answer)
    except Exception as es:
        print(es)

client.run(config.discord_token)