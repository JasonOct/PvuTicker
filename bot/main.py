import os, random, asyncio
import discord
from discord.ext import commands
import httpx
from discord_slash import SlashCommand, SlashContext
from tabulate import tabulate
import numpy as np

client = commands.Bot(command_prefix="$")
slash = SlashCommand(client, sync_commands=True)

coingecko = "https://api.coingecko.com/api/v3/simple/price?ids=plant-vs-undead-token&vs_currencies=usd,bnb"
WAIT_DURATION = int(os.environ['WAIT_DURATION'])
TOKEN = os.environ['DISCORD_TOKEN']
alertValues = []
alertValuesUsers = []
alertValuesUsersIDs = []


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print(f"$ {getPvuPerUSD()} - BNB {getPvuPerBNB()}")
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
        alertValuesTemp = alertValues.astype(np.float)
        i = 0;
        for x in alertValuesTemp:
            if previousPVUUSDT > currentPVUUSDT:
                if x >= currentPVUUSDT:
                    userToBeMentioned = client.get_user_info(int(alertValuesUsersIDs[x]))
                    client.get_channel(877632850130776084).send(userToBeMentioned.mention + ", your target price at " + "${:.2f}".format(x) + " has been reached. Current PVU/USDT rate: " + "${:.2f}".format(currentPVUUSDT))
                    alertValues.pop(i)
                    alertValuesUsers.pop(i)
                    alertValuesUsersIDs.pop(i)
            elif previousPVUUSDT < currentPVUUSDT:
                if x <= currentPVUUSDT:
                    userToBeMentioned = client.get_user_info(int(alertValuesUsersIDs[x]))
                    client.get_channel(877632850130776084).send(userToBeMentioned.mention + ", your target price at " + "${:.2f}".format(x) + " has been reached. Current PVU/USDT rate: " + "${:.2f}".format(currentPVUUSDT))
                    alertValues.pop(i)
                    alertValuesUsers.pop(i)
                    alertValuesUsersIDs.pop(i)

        previousPVUUSDT = currentPVUUSDT()
        await asyncio.sleep(WAIT_DURATION)
        

@client.command(
	help="Looks like you need some help.",
	brief="Sets a price alert"
)
async def alert(ctx, targetValue):
    alertValues.add(targetValue)
    alertValuesUsers.add(ctx.message.author.name)
    alertValuesUsersIDs.add(ctx.message.author.id)
    await ctx.channel.send("{} PVU/USDT price alert set at $".format(ctx.message.author.mention) + targetValue)
    
@client.command(
	help="Looks like you need some help.",
	brief="Show current price alerts"
)
async def showalerts(ctx, targetValue):
    dataToPrint = [alertValues, alertValuesUsers]
    await ctx.channel.send(tabulate(dataToPrint, headers=["Price Alert", "Set by"]))
    
@client.command(
	help="Looks like you need some help.",
	brief="Remove price alerts set by you."
)
async def removemyalerts(ctx, targetValue):
    newAlertValues = alertValues
    newAlertValuesUsers = alertValuesUsers
    newAlertValuesUsersIDs = alertValuesUsersIDs
    deletedAlertValues = []
    deletedAlertValuesUsers = []
    deletedAlertValuesUsersIDs = []
    i = 0;
    for x in alertValuesUsersIDs:
        if x == ctx.message.author.id:
            deletedAlertValues.add( newAlertValues.pop(i) )
            deletedAlertValuesUsers.add( newAlertValuesUsers.pop(i) )
            deletedAlertValuesUsersIDs.add( newAlertValuesUsersIDs.pop(i) )
        
        i = i+1;
    
    AlertValues = newAlertValues
    AlertValuesUsers = newAlertValuesUsers
    AlertValuesUsersIDs = newAlertValuesUsersIDs
    
    dataToPrint = [deletedAlertValues, deletedAlertValuesUsers]
    await ctx.channel.send("The following price alerts were removed: \n" + tabulate(dataToPrint, headers=["Price Alert", "Set by"]))

@client.command(
	help="Looks like you need some help.",
	brief="Remove all price alerts."
)
async def removeallalerts(ctx, targetValue):
    alertValues.clear()
    alertValuesUsers.clear()
    alertValuesUsersIDs.clear()
    await ctx.channel.send("All price alerts have been removed.")
    

client.run(TOKEN)