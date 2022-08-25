import requests, colorama, ctypes, threading, re, json, time, os, json, datetime, discord, copy
from discord.ext import commands
from collections import Counter

# to change the amount of proofs it can find using 'more', go down to line 184

bot = commands.Bot(command_prefix='.')

itemDetails = None
acroToName = {}
nameToAcro = {}
noAcronym = {}
symbols = '`~!@#$%^&*()_-=+[]}{\/|;:,.<>?'

auth = 'your discord ACCOUNT token, it must be in rolimons server'
token = 'your discord BOT token'

headers = {
    'authorization': auth
    }

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

def rolimons(): # yes i didn't use the api, i can't be bothered to change
    global itemDetails, itemNames, nameToAcro, acroToName, noAcronym
    while True:
        try:
            itemDetails = json.loads(
                re.findall('item_details = (.*?);', requests.get('https://www.rolimons.com/itemtable').text)[0]
            )
            for item in itemDetails:
                acronym = itemDetails[item][15]
                name = itemDetails[item][0]
                if acronym != None:
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

    if amount > 1 or amount == 0:
        if amount > 1:
            embed = discord.Embed(title=f"{amount} different limiteds contained '{args}'.\nRetry being more specific (use acronym if there is one)", color=0xff0000)
        elif amount == 0:
            embed = discord.Embed(title=f"Unable to find limited fitting the name/acronym '{args}'", color=0xff0000)
        await ctx.channel.send(embed=embed)
        return None

    foundProofs = 0
    foundProofsTotal = 0
    proofsToFind = 5

    [itemName := itemName.replace(s, '') for s in symbols]
    itemName = itemName.replace('  ', ' ')
    while True:
        if itemAcronym == 'op' or itemAcronym == 'vs':
            r = requests.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemName}&offset={offset}', headers=headers).json()
        else:
            if itemAcronym != None: r = requests.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemAcronym}&offset={offset}', headers=headers).json()
            elif itemAcronym == None: r = requests.get(f'https://discord.com/api/v9/guilds/415246288779608064/messages/search?channel_id=535250426061258753&content={itemName}&offset={offset}', headers=headers).json()

        if r['total_results'] == 0 or r['messages'] == []:
            embed = discord.Embed(title='Unable to find more proofs for this item', color=0xFF0000)
            await ctx.channel.send(embed=embed)
            return None

        for proof in r['messages']:
            try:
                image = proof[0]['attachments'][0]['url']
                time = str(proof[0]['timestamp']).split('T')[0]
                message = proof[0]['content']
                original_message = message.splitlines()
                split_message = proof[0]['content'].lower().splitlines()
                first_line = split_message[0]
                [first_line := first_line.replace(s, '') for s in symbols]
                first_line = first_line.replace('  ', ' ')

                opAmount = ''
                if 'op' in split_message[1] or ' v ' in split_message[1] or ' vs ' in split_message[1] or 'lb' in split_message[1] or 'vs' in split_message[1] or 'lowball' in split_message[1]:
                    opAmount = split_message[1]

                year, month, day = time.split('-')
                if len(day) == 2:
                    if day[0] == '0':
                        day = day.replace('0', '')
                if len(month) == 2:
                    if month[0] == '0':
                        month = month.replace('0', '')
                phrase = f'{day} {months[month]} {year}'

                if itemAcronym != None:
                    if len(itemAcronym.split()) > 1:
                        if len(set(itemAcronym.split())&set(first_line.split())) == len(itemAcronym.split()): pass
                        elif len(set(itemName.split())&set(first_line.split())) == len(itemName.split()): pass
                        else: continue
                    else:
                        if len(set(itemAcronym.split())&set(first_line.split())) == 1: pass
                        elif len(set(itemName.split())&set(first_line.split())) == len(itemName.split()): pass
                        else: continue


                elif itemAcronym == None:
                    if len(set(itemName.split())&set(first_line.split())) == len(itemName.split()): pass
                    else: continue

                #for i in original_message.copy(): # this basically just removes the comment from the message
                #    if len(i) >= 50:
                #        original_message.remove(i)
                #    elif 'comment' in i.lower():
                #        original_message.remove(i)

                original_message = '\n'.join(original_message)

                embed = discord.Embed(title='Click for image', url=image, color=0x4042CE)
                embed.add_field(name=phrase, value=original_message, inline=True)
                if opAmount != '': embed.add_field(name='Proof Amount', value=split_message[1], inline=True)
                embed.set_thumbnail(url=image)
                await ctx.channel.send(embed=embed)
                [(foundProofs := foundProofs + 1, foundProofsTotal := foundProofsTotal + 1)]

                if foundProofs == 5:
                    if foundProofsTotal == 20: return None # 20 is the maximum proofs they can see, just change the number to whatever max amount
                    embed = discord.Embed(title="Found 5 most recent proofs, to see another 5 type 'more'", color=0x0f661b)
                    await ctx.channel.send(embed=embed)
                    def check(c):
                        if c.author == ctx.author:
                            return c.content, c.channel
                    msg = await bot.wait_for('message', check=check)
                    if msg.content.lower() == 'more': foundProofs -= 5; proofsToFind += 5; continue
                    else: return None


            except Exception as err:
                print(err)
                print('Error, this is most likely due to the proof formatted incorrectly')
                pass

        if foundProofs & 5 != 0 or foundProofs == 0 or foundProofsTotal != proofsToFind:
            offset += 25
            continue

        break

bot.run(token)
