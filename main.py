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
    if any(ctx.channel.id == int(i) for i in config['ignoreChannels']): return None
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

        if 'You are being rate limited.' in str(r):
            embed = discord.Embed(title = 'Ratelimited', description = f'Retrying in 15 seconds', color = 0xf08a00)
            await ctx.channel.send(embed=embed)
            time.sleep(15)
            continue

        if r['total_results'] == 0 or r['messages'] == []:
            embed = discord.Embed(title = 'No proofs', description = f'Unable to find *more* proofs for `{args}`', color = 0xFF0000)
            await ctx.channel.send(embed=embed)
            return None

        for proof in r['messages']:
            try:
                if proof[0]['author']['id'] != '1034147338689724508':
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
                else:
                    firstLine = firstLineGrab([proof[0]['embeds'][0]['description'].lower().replace('**', '').split('item: ')[1].split('\n')[0]])

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
                    

                    embed = discord.Embed(color = 0x000000)
                    imageUrl = proof[0]['embeds'][0]['image']['proxy_url']
                    datePhrase, opAmount = Tools.filter(proof[0]['timestamp'], None)
                    opAmount = proof[0]['embeds'][0]['description'].lower().split('**value**: ')[1].split('\n')[0]
                    opAmount = f'\n\n**Proof Amount**\n{opAmount}'
                    embed.add_field(name = datePhrase, value = proof[0]['embeds'][0]['description'], inline = True)
                    embed.add_field(name = 'Image URL', value = f'[Click Here]({imageUrl}){opAmount}')
                    footer = proof[0]['embeds'][0]['description'].lower().split('\n')[0].replace('<', '').replace('>', '').replace('@!', '')
                    embed.set_footer(text=f"Blacklisted {footer}")
                    embed.set_thumbnail(url = imageUrl)
                await ctx.channel.send(embed=embed)
                [(foundProofs := foundProofs + 1, foundProofsTotal := foundProofsTotal + 1)]

                if foundProofs == 5:
                    if foundProofsTotal == config['maxProofs']: return None # 20 is the maximum proofs they can see, just change the number to whatever max amount
                    embed = discord.Embed(title = "Found recent proofs", description = 'To see the next 5 proofs, type `more` in chat (maximum 20).\nIf nothing happened, re-type it', color = 0x0085FF)
                    await ctx.channel.send(embed=embed)

                    def check(c):
                        if c.author == ctx.author:
                            return c.content, c.channel

                    msg = await bot.wait_for('message', check=check)
                    if msg.content.lower() == 'more': foundProofs -= 5; proofsToFind += 5; continue
                    else: return None

            except:
                pass

        if foundProofs & 5 != 0 or foundProofs == 0 or foundProofsTotal != proofsToFind:
            offset += 25
            continue
        break

bot.run(config['discordBotToken'])
