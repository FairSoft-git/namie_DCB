import discord
import json
import os
import tqdm


# create an instance of the client
client = discord.Client()

# If there are no json files, set them up.
try:
    open("prohibitedwords.json", "r")
except:
    print("Creating prohibitedwords.json")
    open("prohibitedwords.json", "w")
try:
    open("config.json", "r")
except:
    print("Creating config.json")
    open("config.json", "w")

# get the data from the .json files
with open("prohibitedwords.json", "r") as fh:
    prohibited_words = json.load(fh)
with open("config.json", "r") as fh:
    botconfig = json.load(fh)


def isValid(username:str) -> bool:

    for word in tqdm.tqdm(prohibited_words, desc="Checking..."):
        if word.strip().lower() in username.strip().lower():
            return False

    return True

def createerror(Desc:str = "", Fields:list= [], Footer:str = ""):
    embed = discord.Embed(
        title="ERROR",
        description=Desc,
        colour=discord.Colour.red()
    )

    embed.set_footer(text=Footer)

    for x in Fields:
        embed.add_field(name=x[0], value=x[1], inline=True)

    return embed

def createwarning(Title:str, Desc:str = "", Fields:list = [], Footer:str = "") -> discord.Embed:
    embed = discord.Embed(
        title = Title,
        description = Desc,
        colour = discord.Colour.orange()
    )

    embed.set_footer(text=Footer)

    for x in Fields:
        embed.add_field(name = x[0], value=x[1], inline=True)

    return embed

def createembed(Title:str = "", Desc:str = "", Fields:list = [], Footer:str = "") -> discord.Embed:
    embed = discord.Embed(
        title = Title,
        description = Desc,
        colour = discord.Colour.blue()
    )

    embed.set_footer(text=Footer)

    for x in Fields:
        embed.add_field(name = x[0], value=x[1])

    return embed

async def updateStatus() -> None:
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"{botconfig['prefix']}help"))

@client.event
async def on_ready():
    print("Ready.")
    await updateStatus()
    return

@client.event
async def on_guild_remove(guild):
    await guild.system_channel.send(embed=createembed("BYE!", "It's been fun!", [["`In case you want me back...`", f"[Here]({botconfig['invite']}) is my invite link!"]]))

@client.event
async def on_member_join(member:discord.Member):

    if not isValid(member.display_name):
        await client.get_channel(botconfig["admin-channel-id"]).send(embed=createembed("WARNING", "A user tripped the alarm.", [["`Mention`", f"{member.mention}"], ["`ID`", f"{member.id}"]]))

    return

@client.event
async def on_message(message:discord.Message):

    # get global variables
    global botconfig
    global prohibited_words

    # return if seeing own message
    if message.author == client.user:
        return

    # if not called, or if called by an invalid user, return
    prefix = botconfig["prefix"]
    if not message.content.startswith(prefix):
        return

    appinfo = await client.application_info()
    if not message.author.id in botconfig["admin-ids"] and not message.author == appinfo.owner:
        await message.channel.send(embed=createerror("You don't have permission to use that command!", ["`Suggestion`", "If you think this is a mistake, please contact a server admin."]))
        return

    # Owner commands
    if message.author == appinfo.owner:
        if message.content.startswith(f"{prefix}restart"):
            if not message.author == appinfo.owner:
                await message.channel.send("Permission denied.")
                await message.channel.send(embed=createerror("You don't have permission to use that command!", [["`Suggestion`", "If you think this is a mistake, try debugging the bot."]]))
            x = __file__.split('\\')[len(__file__.split('\\')) - 1]
            print("Restarting...")
            await message.channel.send("Restarting...")
            os.system(f"{x}")
            return

        elif message.content.startswith(f"{prefix}test"):
            adminchannel = client.get_channel(botconfig["admin-channel-id"])
            valid = isValid(appinfo.owner.display_name)
            await adminchannel.send(f"Validity: {valid}")
            await adminchannel.send(embed=createwarning("TEST - NO ACTION REQUIRED", "User tripped the bot. Please check.", [["`Mention`", appinfo.owner.mention], ["`ID`", appinfo.owner.id]]))
            return

    # general commands
    if message.content.startswith(f"{prefix}help"):
        await message.channel.send(embed=createembed("HELP", f"Commands for {client.user.display_name}", [[f"`{prefix}help`", "Display this help menu."],
                                                                                                          [f"`{prefix}prohibit [PHRASE]`", "Prohibits [PHRASE]."],
                                                                                                          [f"`{prefix}allow [PHRASE]`", "Allows [PHRASE]."],
                                                                                                          [f"`{prefix}prefix [NEWPREFIX]`", "Sets the prefix to [NEWPREFIX]."]]))
        return

    elif message.content.startswith(f"{prefix}prohibits"):
        words = ""
        for word in prohibited_words:
            words += f"{word}\n"

        try:
            await message.channel.send(embed=createembed("INFORMATION", "List of prohibited phrases", [["`List:`", words]]))
        except discord.errors.HTTPException as e:
            await message.channel.send(embed=createerror(
                "Error while fetching prohibited words. Case may be that there are no prohibited words.",
                [["`Exception`", f"{e}"]]))

    elif message.content.startswith(f"{prefix}prohibit"):


        prohibited_words.append(message.content.replace(f"{prefix}prohibit ", ""))

        with open("prohibitedwords.json", "w") as fh:
            json.dump(prohibited_words, fh)

        await message.channel.send(embed=createembed("INFORMATION", f"We now prohibit \"{message.content.replace(f'{prefix}prohibit ', '')}\""))


        return

    elif message.content.startswith(f"{prefix}allow "):

        try:
            prohibited_words.remove(message.content.replace(f'{prefix}allow ', ''))
        except:
            await message.channel.send("This phrase was not prohibited.")
            return

        with open("prohibitedwords.json", "w") as fh:
            json.dump(prohibited_words, fh)
        with open("prohibitedwords.json", "r") as fh:
            prohibited_words = json.load(fh)

        await message.channel.send(embed=createembed("INFORMATION", f"We no longer prohibit {message.content.replace(f'{prefix}allow ', '')}"))

        return



    elif message.content.startswith(f"{prefix}prefix"):

        botconfig["prefix"] = message.content.replace(f"{prefix}prefix ", "")

        with open("config.json", "w") as fh:
            json.dump(botconfig, fh)
        with open("config.json", "r") as fh:
            botconfig = json.load(fh)

        await message.channel.send(embed=createembed("INFORMATION", "Prefix updated!", [["`New prefix", f"{botconfig['prefix']}"]]))


        await updateStatus()

        return

    # If not valid command, display error
    else:
        await message.channel.send(embed=createerror("Command not found", [["`Suggestion`", f"Use `{prefix}help` for a list of commands."]]))


    return

client.run(botconfig["token"])