import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
from math import *

###################################################
# Bank Ore Data Management

def save_data(data): # Gemmer data i save.json
    with open('Discord Bot/save.json', 'w') as f:
        json.dump(data, f)

def reset_save(password): # Sletter alt gemt data. Kræver et password for ekstra sikring
    if password == 'SilasErSej':
        data = {}
        for i in [['copper', 0.5, 0.125, 0.5], ['coal', 0.5, 0.125, 0.5], ['iron', 2, 0.0625, 2], ['gold', 4, 0.5, 4], ['redstone', 2, 0.25, 2], ['lapis', 3, 0.3, 3], ['diamond', 40, 16, 10], ['netherite', 240, 80, 60]]:
            data[i[0]] = {'inventory': 0, 'price': None, 'base_price': i[1], 'minimum': i[2], 'base_weight': i[3], 'local_weight': 0, 'percent': 0}
        save_data(data=data)
        update_data()
    else:
        print('Password er forkert')

def get_data(ore):  # Returnere al data omkring 1 specificeret ore
    with open('Discord Bot/save.json', 'r') as f:
        data = json.load(f)
        return data[ore]
    
def change_inventory(ore, amount):  # Ændre antallet af ores i deres inventory. Tager ikke hensyn til prisskift undervejs, så burde kun ændres med 1 ad gangen
    with open('Discord Bot/save.json', 'r') as f:
        data = json.load(f)
    data[ore]['inventory'] += amount
    save_data(data=data)
    update_data()

def update_data(): # Opdaterer alle priser, procenter og locale vægtninger i save.json. Køres automatisk i slutningen af change_inventory
    with open('Discord Bot/save.json', 'r') as f:
        data = json.load(f)
    for i in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']:
        data[i]['local_weight'] = (data[i]['inventory'] + 1) * data[i]['base_weight']

    weight_sum = sum([data[i]['local_weight'] for i in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']])
    inventory_sum = sum([data[i]['inventory'] for i in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']]) + 1
    for i in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']:
        b = data[i]['base_price']
        m = data[i]['minimum']
        l = data[i]['local_weight']
        data[i]['price'] = m * (l / weight_sum)**(log(b/m) / log(0.125))

        data[i]['percent'] = data[i]['inventory'] / inventory_sum
    save_data(data=data)

def print_data(): # Printer Data fra save.json i formatet "ORE: Inventory: {},    Price: {},     Percent: {}%\n"
    with open('Discord Bot/save.json', 'r') as f:
        data = json.load(f)
    strings = []
    for i in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']:
        strings.append(f"{i.upper()}:    Inventory: {data[i]['inventory']},     Price: {round(data[i]['price'], 2)},    Percent: {round(100 * data[i]['percent'], 1)}%")
    for i in strings:
        print(i)
    return strings

###############################################

###############################################
# Player account data management

def save_accounts(data):
    with open('Discord Bot/accounts.json', 'w') as f:
        json.dump(data, f)

def reset_accounts(password):
    if password == 'SilasErSej':
        save_accounts({})
    else:
        print("Password er forkert")

def get_all_accounts():
    with open('Discord Bot/accounts.json', 'r') as f:
        return json.load(f)
    
def get_account(name):
    account = get_all_accounts()[name]
    return account

###############################################

if False:
    reset_accounts('SilasErSej')
    reset_save('SilasErSej')

###############################################
# Discord Bot Startup
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
###############################################

###############################################
# Bot Events

@bot.event
async def on_ready():
    print(f"We're ready - {bot.user.name}")

###############################################


###############################################
# Bot Commands

@bot.command() # Viser en liste af alle kommandoer
async def hjælp(ctx):
    await ctx.channel.send("""Hjælpeliste til alle kommandoer du kan lave\n
                            - /deposit {ore} {antal}\nDeposit kommandoen bruges når du vil lægge ores ind i banken\nEksempel: /deposit iron 128\n
                            - /rates\nRates kommandoen viser nuværende priser på alle ores\n
                            - /account\nAccount kommandoen fortæller dig din saldo\n
                            - /withdraw {ore} {antal}\nWithdraw kommandoen bruges når du vil hæve ores fra banken\nEksempel: /withdraw diamond 2\n
                            - /pay {konto} {antal}\nPay kommandoen bruges når du vil betale penge til andre\nEksempel: /pay silasduus 1000""")

@bot.command() # Indlægger ores til banken
async def deposit(ctx, *, msg):
    try:
        msg = msg.split()
    except:
        msg = ['']
    if len(msg) >= 2:
        if msg[0].lower() in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']:
            try:
                msg[1] = int(msg[1])
            except:
                pass
            if isinstance(msg[1], int):
                if msg[1] <= 64 * 9 * 6 and msg[1] >= 1:
                    acc = 0
                    for i in range(int(msg[1])):
                        data = get_data(msg[0])
                        acc += data['price']
                        change_inventory(msg[0], 1)
                    acc = round(acc)
                    print_data()
                    data = get_all_accounts()
                    if ctx.author.name in data:
                        data[ctx.author.name] += acc
                    else:
                        data[ctx.author.name] = acc
                    save_accounts(data)
                    await ctx.channel.send(f"{ctx.author.mention} vil gerne indlægge {msg[1]} {msg[0]} i banken\nDet får du {acc} coins for!")
                    return
                else:
                    await ctx.channel.send(f"{msg[1]} er enten for høj eller for lav. Du kan kun indsætte værdier mellem 1 og {64 * 9 * 6} (Det er en fuld dobbeltkiste).")
            else:
                await ctx.channel.send(f"Du skal bruge et heltal som værdi. Du brugte {msg[1]}.")
        else:
            await ctx.channel.send(f"Du skal bruge en ore fra denne liste: copper, coal, iron, gold, redstone, lapis, diamond eller netherite. Du brugte {msg[0]}.")
    else:
        await ctx.channel.send("Du har ikke indskrevet nok argumenter i kommandoen. Kommandoen skal skrives på formen /deposit {ore} {antal}.")

@bot.command() # Hæver ores fra banken
async def withdraw(ctx, *, msg):
    msg = msg.split()
    if len(msg) >= 2:
        if msg[0].lower() in ['copper', 'coal', 'iron', 'gold', 'redstone', 'lapis', 'diamond', 'netherite']:
            data = get_data(msg[0])
            start_inventory = data['inventory']
            try:
                msg[1] = int(msg[1])
            except:
                await ctx.channel.send(f"Du skal bruge et heltal som værdi. Du brugte {msg[1]}.")
                return
            if msg[1] <= start_inventory:
                if msg[1] >= 1:

                    acc = 0
                    for i in range(msg[1]):
                        data = get_data(msg[0])
                        acc += data['price']
                        change_inventory(msg[0], -1)
                    
                    acc = round(acc)
                    if acc > get_account(ctx.author.name):
                        change_inventory(msg[0], start_inventory)
                        await ctx.channel.send(f"Du har ikke råd til dette. Det koster {acc}. Du har {get_account(ctx.author.name)}.")
                        return
                    accounts = get_all_accounts()
                    accounts[ctx.author.name] -= acc
                    save_accounts(accounts)
                    await ctx.channel.send(f"{ctx.author.mention} har nu hævet {msg[1]} {msg[0]} fra banken. Det kostede dig {acc} coins.")
                else: await ctx.channel.send(f"Du kan ikke hæve mindre end 1 ore.")
            else: await ctx.channel.send(f"Der er ikke nok {msg[0]} i banken. Der er kun {start_inventory}.")
        else: await ctx.channel.send(f"Du skal bruge en ore fra denne liste: copper, coal, iron, gold, redstone, lapis, diamond eller netherite. Du brugte {msg[0]}.")
    else: await ctx.channel.send("Du har ikke indskrevet nok argumenter i kommandoen. Kommandoen skal skrives på formen /withdraw {ore} {antal}.")
    
@bot.command() # Viser de nuværende rater på alle ores
async def rates(ctx):
    data = print_data()
    await ctx.channel.send(''.join([f'{i}\n' for i in data]))

@bot.command() # Viser din saldo
async def account(ctx):
    all = get_all_accounts()
    if ctx.author.name in all:
        await ctx.channel.send(f"{ctx.author.mention} saldo er {get_account(ctx.author.name)}!")
    else:
        all[ctx.author.name] = 0
        print(all)
        save_accounts(all)
        await ctx.channel.send(f"{ctx.author.mention} har ikke en konto. Du har nu fået en konto. Din saldo er {get_account(ctx.author.name)}!")

@bot.command()
async def pay(ctx, *, msg):
    msg = msg.split()
    if len(msg) < 2:
        await ctx.channel.send("Du har ikke indskrevet nok argumenter i kommandoen. Kommandoen skal skrives på formen /pay {person} {amount}.")
        return
    try:
        msg[1] = int(msg[1])
    except:
        await ctx.channel.send(f"Du skal bruge et heltal som værdi. Du brugte {msg[1]}.")
        return
    if not msg[0] in get_all_accounts():
        await ctx.channel.send(f"{msg[0]} har ikke en konto.")
        return
    if not ctx.author.name in get_all_accounts():
        await ctx.channel.send(f"Du har ikke en konto.")
        return
    if get_account(ctx.author.name) < msg[1]:
        await ctx.channel.send(f"Du har ikke nok penge på din konto.")
        return
    if msg[1] < 1:
        await ctx.channel.send(f"Du kan ikke give mindre end 1 coin.")
        return
    all = get_all_accounts()
    all[ctx.author.name] -= msg[1]
    all[msg[0]] += msg[1]
    save_accounts(all)
    await ctx.channel.send(f"{ctx.author.mention} har betalt {msg[0]} {msg[1]} coins!")

###############################################

bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)