import requests, threading, json, time, json, discord
from discord.ext import commands
from misc import Tools
session = requests.Session()

with open('config.json') as config:
    config = json.load(config)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
session.headers['authorization'] = config['discordAccountToken']

itemDetails = None
acroToName = {}
nameToAcro = {}
noAcronym = {}
assetIds = {}

def firstLineGrab(splitMessage):
    firstLine = splitMessage[0].replace('  ', ' ')
    for i in '`~!@#$%^&*()_-=+[]}{\/|;:,.<>?':
        firstLine = firstLine.replace(i, '')
    firstLine = firstLine.replace('  ', ' ')
    return firstLine

def rolimons():
    global itemDetails, itemNames, nameToAcro, acroToName, noAcronym, assetIds
    while True:
        assetIds, nameToAcro, acroToName, noAcronym = Tools.roli()
        if nameToAcro != None: time.sleep(600)
        else: time.sleep(60)
threading.Thread(target=rolimons).start()

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(color=0xf08a00)
    embed.add_field(name='Error', value=error)
    await ctx.channel.send(embed=embed)

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def proof(ctx, *, args):
    itemName, itemAcronym, amount = Tools.findItem(args, acroToName, nameToAcro, noAcronym)
    offset = 0

    if amount != 1:
        if amount > 1: embed = discord.Embed(title = 'Not specific enough', description = f'`{args}` matched with multiple other limiteds, retry using the limited acronym or **full** name', color = 0xff0000)
        elif amount == 0: embed = discord.Embed(title = "No found limited", description = f'Unable to find limited to match with `{args}`', color = 0xff0000)
        await ctx.channel.send(embed=embed)
        return None

    foundProofs = 0
    foundProofsTotal = 0
    proofsToFind = 5

    while True:
        content = Tools.toUse(itemAcronym, itemName)
        r = session.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={content}&offset={offset}').json()

        if r['total_results'] == 0 or r['messages'] == []:
            embed = discord.Embed(title = 'No proofs', description = f'Unable to find *more* proofs for `{args}`', color = 0xFF0000)
            await ctx.channel.send(embed=embed)
            return None

        for proof in r['messages']:
            try:
                imageUrl = proof[0]['attachments'][0]['url']
                Message = proof[0]['content']
                splitMessage = Message.lower().splitlines()
                firstLine = firstLineGrab(splitMessage)

                if itemAcronym != None:
                    if len(itemAcronym.split()) > 1:
                        if len(set(itemAcronym.split())&set(firstLine.split())) == len(itemAcronym.split()): pass
                        elif len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                        else: continue
                    else:
                        if len(set(itemAcronym.split())&set(firstLine.split())) == 1: pass
                        elif len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                        else: continue


                elif itemAcronym == None:
                    if len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                    else: continue

                embed = discord.Embed(color = 0x4042CE)
                datePhrase, opAmount = Tools.filter(proof[0]['timestamp'], splitMessage)
                embed.add_field(name = datePhrase, value = Message, inline = True)
                embed.add_field(name = 'Image URL', value = f'[Click Here]({imageUrl}){opAmount}')
                embed.set_thumbnail(url = imageUrl)
                await ctx.channel.send(embed=embed)
                [(foundProofs := foundProofs + 1, foundProofsTotal := foundProofsTotal + 1)]

                if foundProofs == 5:
                    if foundProofsTotal == 20: return None # 20 is the maximum proofs they can see, just change the number to whatever max amount
                    embed = discord.Embed(title = "Found recent proofs", description = 'To see the next 5 proofs, type `more` in chat (maximum 20).\nIf nothing happened, re-type it', color = 0x0085FF)
                    await ctx.channel.send(embed=embed)

                    def check(c):
                        if c.author == ctx.author:
                            return c.content, c.channel

                    msg = await bot.wait_for('message', check=check)
                    if msg.content.lower() == 'more': foundProofs -= 5; proofsToFind += 5; continue
                    else: return None

            except Exception as err:
                print(err)
                pass

        if foundProofs & 5 != 0 or foundProofs == 0 or foundProofsTotal != proofsToFind:
            offset += 25
            continue
        break

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def often(ctx, *, args):
    itemName, itemAcronym, amount = Tools.findItem(args, acroToName, nameToAcro, noAcronym)

    if amount != 1:
        if amount > 1: embed = discord.Embed(title = 'Not specific enough', description = f'`{args}` matched with multiple other limiteds, retry using the limited acronym or **full** name', color = 0xff0000)
        elif amount == 0: embed = discord.Embed(title = "No found limited", description = f'Unable to find limited to match with `{args}`', color = 0xff0000)
        await ctx.channel.send(embed=embed)
        return None

    offset = 0
    timeStamps = []
    imageUrl = requests.get(f'https://thumbnails.roblox.com/v1/assets?assetIds={assetIds[str(itemName)]}&returnPolicy=0&size=250x250&format=Png&isCircular=false').json()['data'][0]['imageUrl']

    while len(timeStamps) != 10:
        content = Tools.toUse(itemAcronym, itemName)
        r = session.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={content}&offset={offset}').json()

        if r['total_results'] == 0 or r['messages'] == []:
            break

        else:
            for proof in r['messages']:
                if len(timeStamps) != 10:
                    try:
                        Message = proof[0]['content']
                        splitMessage = Message.lower().splitlines()
                        firstLine = firstLineGrab(splitMessage)

                        if itemAcronym != None:
                            if len(itemAcronym.split()) > 1:
                                if len(set(itemAcronym.split())&set(firstLine.split())) == len(itemAcronym.split()): pass
                                elif len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                                else: continue
                            else:
                                if len(set(itemAcronym.split())&set(firstLine.split())) == 1: pass
                                elif len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                                else: continue


                        elif itemAcronym == None:
                            if len(set(itemName.split())&set(firstLine.split())) == len(itemName.split()): pass
                            else: continue

                        timeStamps.append(proof[0]['timestamp'])
                    except:
                        pass
            offset += 25

    if len(timeStamps) >= 2:
        filteredDates, sinceRecent, betweenDates = Tools.checkDates(timeStamps)
        embed = discord.Embed(title = args, description = f'days between the {len(filteredDates)} recent proofs: **{betweenDates}**\ndays since the most recent proof: **{sinceRecent}**', color = 0x4042CE)
        embed.set_thumbnail(url = imageUrl)
        await ctx.channel.send(embed=embed)
    elif len(timeStamps) == 1:
        filteredDates, sinceRecent, betweenDates = Tools.checkDates(timeStamps)
        embed = discord.Embed(title = args, description = f'managed to only find **1** proof. unable to continue', color = 0x4042CE)
        embed.set_thumbnail(url = imageUrl)
        await ctx.channel.send(embed=embed)
    else:
        embed = discord.Embed(title = 'No proofs', description = f'Unable to find *more* proofs for `{args}`', color = 0xFF0000)
        embed.set_thumbnail(url = imageUrl)
        await ctx.channel.send(embed=embed)

bot.run(config['discordBotToken'])
