import requests, colorama, ctypes, threading, re, json, time, os, json, datetime, discord, copy
from discord.ext import commands
from collections import Counter

discord_bot_token = 'put token in here!'
discord_account_token = 'put token in here!' # your account has to be in the rolimons discord server or it will not work

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
session = requests.Session()
session.headers['authorization'] = discord_account_token

itemDetails = None
acroToName, nameToAcro, noAcronym = {}, {}, {}
symbols = '`~!@#$%^&*()_-=+[]}{\/|;:,.<>?'

months = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
    }

def firstLineGrab(splitMessage):
    firstLine = splitMessage[0].replace('  ', ' ')
    for i in symbols:
        firstLine = firstLine.replace(i, '')
    return firstLine

def rolimons():
    global itemDetails, itemNames, nameToAcro, acroToName, noAcronym
    while True:
        try:
            itemDetails = requests.get(
                'https://www.rolimons.com/itemapi/itemdetails'
            ).json()['items']
            for item in itemDetails:
                acronym = itemDetails[item][1]
                name = itemDetails[item][0]
                if acronym != '':
                    nameToAcro[name] = [acronym]
                    acroToName[acronym] = [name]
                else:
                    if len(name.split()) == 1:
                        acroToName[name] = [name]
                        nameToAcro[name] = [name]
                    else:
                        noAcronym[name] = None
            time.sleep(600)
        except:
            time.sleep(60)
            continue

threading.Thread(target=rolimons).start()

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(color=0xf08a00)
    embed.add_field(name='Error', value=error)
    await ctx.channel.send(embed=embed)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def proof(ctx, *, args):
    itemName, itemAcronym, amount, offset = None, None, 0, 0

    for i in acroToName:
        if args.lower() == i.lower():
            amount += 1
            itemAcronym = i.lower()
            itemName = acroToName[i][0].lower()

    if amount == 0:
        for i in nameToAcro:
            if args.lower() == i.lower():
                amount += 1
                itemName = i.lower()
                itemAcronym = nameToAcro[i][0].lower()

    if amount == 0:
        for i in nameToAcro:
            if args.lower() in i.lower():
                amount += 1
                itemName = i.lower()
                itemAcronym = nameToAcro[i][0].lower()

    if amount == 0:
        for i in noAcronym:
            if args.lower() == i.lower():
                amount += 1
                itemName = i.lower()

    if amount == 0:
        for i in noAcronym:
            if args.lower() in i.lower():
                amount += 1
                itemName = i.lower()

    if amount != 1:
        if amount > 1: embed = discord.Embed(title = 'Not specific enough', description = f'`{args}` matched with multiple other limiteds, retry using the limited acronym or **full** name', color = 0xff0000)
        elif amount == 0: embed = discord.Embed(title = "No found limited", description = f'Unable to find limited to match with `{args}`', color = 0xff0000)
        await ctx.channel.send(embed=embed)
        return None

    foundProofs = 0
    foundProofsTotal = 0
    proofsToFind = 5

    [itemName := itemName.replace(i, '') for i in symbols]
    itemName = itemName.replace('  ', ' ')
    while True:
        if itemAcronym == 'op' or itemAcronym == 'vs':
            r = session.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemName}&offset={offset}').json()
        else:
            if itemAcronym != None: r = session.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemAcronym}&offset={offset}').json()
            elif itemAcronym == None: r = session.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemName}&offset={offset}').json()

        if r['total_results'] == 0 or r['messages'] == []:
            embed = discord.Embed(title = 'No proofs', description = f'Unable to find *more* proofs for `{args}`', color = 0xFF0000)
            await ctx.channel.send(embed=embed)
            return None

        for proof in r['messages']:
            try:
                imageUrl = proof[0]['attachments'][0]['url']
                Year, Month, Date = str(proof[0]['timestamp']).split('T')[0].split('-', 3)
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
                embed.add_field(name = f'{Date} {months[Month.strip("0")]} {Year}', value = Message, inline = True)
                if 'op' in splitMessage[1] or ' v ' in splitMessage[1] or ' vs ' in splitMessage[1] or 'lb' in splitMessage[1] or 'vs' in splitMessage[1] or 'lowball' in splitMessage[1]: opAmount = f'\n\n**Proof Amount**\n{splitMessage[1]}'
                else: opAmount = ''
                embed.add_field(name = 'Image URL', value = f'[Click Here]({imageUrl}){opAmount}')
                embed.set_thumbnail(url = imageUrl)
                await ctx.channel.send(embed=embed)
                [(foundProofs := foundProofs + 1, foundProofsTotal := foundProofsTotal + 1)]

                if foundProofs == 5:
                    if foundProofsTotal == 20: return None # 10 is the maximum proofs they can see, just change the number to whatever max amount
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

bot.run(discord_bot_token)
