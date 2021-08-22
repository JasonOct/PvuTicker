import os, random, asyncio
import discord
from discord.ext import commands
import httpx
from tabulate import tabulate
import numpy as np

client = commands.Bot(command_prefix="$")

coingecko = "https://api.coingecko.com/api/v3/simple/price?ids=plant-vs-undead-token&vs_currencies=usd,bnb"
WAIT_DURATION = 10 #int(os.environ['WAIT_DURATION'])
TOKEN = 'ODc4NTQwNDYwMTk1NDU5MTYy.YSCqkA.LHpC313lRjFhUjy6fx65z62m4X0' #os.environ['DISCORD_TOKEN']
alertValues = []
alertValuesUsers = []
alertValuesUsersIDs = []


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print(f"$ {getPvuPerUSD()} - BNB {getPvuPerBNB()}")
    await client.get_channel(877632850130776084).send("Bot restarted. All price alerts have been removed.")
    asyncio.create_task(taskUpdateActivity())


def getCoingeckoData():
    with httpx.Client(timeout=None) as httpx_client:
        response = httpx_client.get(coingecko)
        data = response.json()
        return data


def getPvuPerUSD():
    return float(getCoingeckoData()["plant-vs-undead-token"]['usd'])


def getPvuPerIDR():
    return float(getCoingeckoData()["plant-vs-undead-token"]['idr'])


def getPvuPerBNB():
    return float(getCoingeckoData()["plant-vs-undead-token"]['bnb'])


async def taskUpdateActivity():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in client.guilds:

            await guild.me.edit(nick="${:.2f}".format(getPvuPerUSD())+"/PVU")

        activityStatus = "{:.2f}".format(getPvuPerBNB()) + " BNB"

        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activityStatus))
        
        currentPVUUSDT = getPvuPerUSD()
        i = 0;
        for x in alertValues:
            if previousPVUUSDT > currentPVUUSDT:
                if float(x) >= currentPVUUSDT:
                    userToBeMentioned = client.get_user_info(int(alertValuesUsersIDs(x)))
                    client.get_channel(877632850130776084).send(userToBeMentioned.mention + ", your target price at " + "${:.2f}".format(float(x)) + " has been reached. Current PVU/USDT rate: " + "${:.2f}".format(currentPVUUSDT))
                    alertValues.remove(i)
                    alertValuesUsers.remove(i)
                    alertValuesUsersIDs.remove(i)
            elif previousPVUUSDT < currentPVUUSDT:
                if float(x) <= currentPVUUSDT:
                    userToBeMentioned = client.get_user_info(int(alertValuesUsersIDs(x)))
                    client.get_channel(877632850130776084).send(userToBeMentioned.mention + ", your target price at " + "${:.2f}".format(float(x)) + " has been reached. Current PVU/USDT rate: " + "${:.2f}".format(currentPVUUSDT))
                    alertValues.remove(i)
                    alertValuesUsers.remove(i)
                    alertValuesUsersIDs.remove(i)

        previousPVUUSDT = currentPVUUSDT
        await asyncio.sleep(WAIT_DURATION)
        

@client.command(
	help="Looks like you need some help.",
	brief="Sets a price alert"
)
async def alert(ctx, targetValue):
    alertValues.append(targetValue)
    print(alertValues)
    alertValuesUsers.append(ctx.message.author.name)
    print(alertValuesUsers)
    alertValuesUsersIDs.append(str(ctx.message.author.id))
    print(alertValuesUsersIDs)
    await ctx.channel.send("{} PVU/USDT price alert set at $".format(ctx.message.author.mention) + targetValue)
    
@client.command(
	help="Looks like you need some help.",
	brief="Show current price alerts"
)
async def showalerts(ctx):
    dataToPrint = zip(alertValues, alertValuesUsers)
    await ctx.channel.send(tabulate(dataToPrint, headers=["Price Alert", "Set by"]))
    
@client.command(
	help="Looks like you need some help.",
	brief="Remove price alerts set by you."
)
async def removemyalerts(ctx):
    deletedAlertValues = []
    deletedAlertValuesUsers = []
    deletedAlertValuesUsersIDs = []
    i = 0;
    for x in alertValuesUsersIDs:
        if int(x) == ctx.message.author.id:
            deletedAlertValues.append( alertValues[i] )
            deletedAlertValuesUsers.append( alertValuesUsers[i] )
            deletedAlertValuesUsersIDs.append( alertValuesUsersIDs[i] )
            alertValues.remove(i)
            alertValuesUsers.remove(i)
            alertValuesUsersIDs.remove(i)
        
        i = i+1;
    
    dataToPrint = [deletedAlertValues, deletedAlertValuesUsers]
    await ctx.channel.send("The following price alerts were removed: \n" + tabulate(dataToPrint, headers=["Price Alert", "Set by"]))

@client.command(
	help="Looks like you need some help.",
	brief="Remove all price alerts."
)
async def removeallalerts(ctx):
    alertValues.clear()
    alertValuesUsers.clear()
    alertValuesUsersIDs.clear()
    await ctx.channel.send("All price alerts have been removed.")
    

client.run(TOKEN)