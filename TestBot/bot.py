from datetime import datetime, timedelta
from google_images_search import GoogleImagesSearch
from io import BytesIO
from PIL import Image
from random import seed, randint
import sys
import discord
from discord.ext import commands
import asyncio
import json
import uuid


# _search_params = {
#     'q': '',
#     'num': 10,
#     'safe': 'high|medium|off',
#     'fileType': 'jpg|gif|png',
#     'imgType': 'clipart|face|lineart|news|photo',
#     'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
#     'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
#     'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
# }

credentials = {}
with open('credentials.json') as json_file:
    credentials = json.load(json_file)

# google image search api init
gis = GoogleImagesSearch(credentials["google-image-api-key"], credentials["google-image-project-cx"])

bot = commands.Bot(command_prefix='!')

tasks = {}

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if(message.author == bot.user):
        return
    await bot.process_commands(message)

@bot.command()
async def test(ctx, *args):
    await ctx.send('{}'.format(*args))

@bot.command()
async def search(ctx, arg1):
    print('Searching {}'.format(arg1))

    #filename=str(uuid.uuid4())
    file = await search_image(arg1, 10)
    await ctx.send(file=file)


async def search_image(search_terms, num):
    gis.search({'q': search_terms, 'num': num})

    results = gis.results()

    print(len(results))
    # get random number
    seed(datetime.now())
    rand_num = randint(0, len(results))

    chosen_image = results[rand_num]

    bytes = BytesIO()

    ## this is kinda fucked, find a better way
    bytes.seek(0)
    raw_image = chosen_image.get_raw_data()
    chosen_image.copy_to(bytes, raw_image)
    bytes.seek(0)
    # to get file format
    temp_image = Image.open(bytes)
    bytes.seek(0)
    format = str.lower(temp_image.format)
    send_file = discord.File(bytes, filename=(str(uuid.uuid4())+'.'+format))
    #filename=str(uuid.uuid4())
    return send_file

@bot.command()
async def cow(ctx, mode, delay: str = str(60*60), startTime: str = None):
    if(mode == 'start'):
        id = ctx.channel.id
        timeStr = []
        if(startTime != None):
            timeStr = startTime.split(':')
            startTime = (int(timeStr[0]), int(timeStr[1]))
            if(len(timeStr) != 2):
                ctx.send('Incorrect time string')
                return
        timeout = int(delay)

        # add a perpertually running task
        tasks["cow"] = bot.loop.create_task(schedule_function(timeout, startTime, send_to_channel, id, 'test-message'))
    if(mode == 'stop'):
        print('Stopping cow task')
        tasks["cow"].cancel()

async def send_to_channel(id, content):
    channel = bot.get_channel(id)
    await channel.send('{0}'.format(content))


async def send_random_cow_image(id):
    a = 1

async def schedule_function(timeout, startTime, function, *args):
    if(startTime != None):
        waitTime = 0
        now = datetime.now()
        calculatedTimeToday = datetime(now.year, now.month, now.day, startTime[0], startTime[1])

        # if time is today or tomorrow
        if(now > calculatedTimeToday):
            scheduledTime = now + timedelta(days=1,hours=startTime[0],minutes=startTime[1])
            waitTime = (scheduledTime - now).total_seconds()
        else:
            waitTime = (calculatedTimeToday - now).total_seconds()

        # wait until next run
        print('Waiting {0} minutes'.format(waitTime/60))
        await asyncio.sleep(waitTime)

    while not bot.is_closed():
        await function(*args)
        await asyncio.sleep(timeout)

bot.run(credentials["discord-bot-token"])
