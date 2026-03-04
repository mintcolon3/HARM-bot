import discord
import json
import os
import random
import math
import typing
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# --------------------------------------------------
# ----------------- CONSTANT DATA ------------------
# --------------------------------------------------

serverID = 1377373701900865666 + 1 # i avoided the number ^w^

harmLines = [
    "JOIN A H.A.R.M. SQUAD",
    "PROTECT YOUR TOWN. PROTECT YOUR SELF.",
    "DON'T PUT OTHERS AT RISK; REPORT ALL CONTRABAND TO YOUR LOCAL H.A.R.M. DIVISION",
    "BREAK THE SEAL; BREAK THE LAW",
    "JOIN H.A.R.M.",
    "REDUCE VOLUME; RESIST VIOLENCE; RETAIN HARMONY",
    "LONG JOURNEY? STAY SAFE. STAY QUIET.",
    "DON'T SING AND DRIVE",
    "YOU CAN'T CARRY A TUNE AND YOUR COMMUNITY",
    "JOIN TODAY",
    "MUSIC WAS NICHE; HARM IS FOR EVERYONE",
    "HARMONY AND RESONANCE MANAGEMENT"
]

expDefault = {
    "lvl" : 0,
    "exp" : 0,
    "msg" : 0,
    "msg-exp" : 0,
    "vc" : 0,
    "vc-exp" : 0,
    "vc-join" : "",
    "bg" : "default",
    "opt" : {
        "ping" : 1
    }
}

expMessage = 5
expVoice = 1.5
expFormula = [20, 4, 2] # A + Bx^C

expRole = {
    1453058381903560715 : 1.2, # member #39                     ; this was loudy but i somehow didnt notice she left until rn i feel so bad :bwuuu:
    1450200155273035899 : 1.2, # slime girl                     ; bwahiro
    1471540171546562693 : 1.2, # lesser princess of bwaa        ; windy
    1474082377172127815 : 1.2  # vc for 300 hours, farming exp  ; minty, an   t, katie she they
}

expChannel = {
    1433530124934053929 : 0 # chain-chat
}

# --------------------------------------------------
# ------------------- LOAD DATA --------------------
# --------------------------------------------------

# Load data from .env file.
load_dotenv()

# Load data from exp.json file.
with open("exp.json") as expFile:
    expData = json.load(expFile)

# --------------------------------------------------
# ------------------- FUNCTIONS --------------------
# --------------------------------------------------


# ---------- EXP SAVE ----------
# Called when any changes are made to expData.

def expSave(expData: dict):
    with open("exp.json", "w") as expFile:
        json.dump(expData, expFile, indent=4)


# ---------- LEVEL UPDATE ----------
# Called when exp is updated, checks if level should also be updated.

async def levelUpdate(user: discord.Member):
    uid = str(user.id)

    currentLevel = expData[uid]["lvl"]
    originalLevel = currentLevel
    isNewLevel = False
    finished = False
    while not finished:
        # Check if current exp is equal to or greater than the next level.
        nextLevelExp = expFormula[0] + ( expFormula[1] * ( (currentLevel+1) ** expFormula[2] ) ) # A + Bx^C
        if expData[uid]["exp"] >= nextLevelExp:
            isNewLevel = True
            currentLevel += 1
        else:
            finished = True
    
    if isNewLevel:
        channel = serverObj.get_channel(1377373703418937477)

        # Check if user has level pings disabled.
        if expData[uid]["opt"]["ping"] == 1:
            desc = f"<@{uid}> is now level **{currentLevel}**"
        else:
            desc = f"{user.display_name} is now level **{currentLevel}**"
        
        if originalLevel == 0:
            desc += "\n-# You can disable level pings by running `$pings`."
        
        await channel.send(desc)
    
    expData[uid]["lvl"] = currentLevel
    return expData
            

# ---------- EXP UPDATE ----------
# Called whenever a user sends a message, joins a VC, or leaves a VC.

async def expUpdate(type: str, user: discord.Member, channelID: int = None, channel: discord.VoiceChannel = None):
    global expData
    uid = str(user.id)

    if type == "message":
        # Calculate new exp to add.
        newExp = expMessage
        for role in user.roles:
            if role.id in expRole.keys():
                newExp *= expRole[role.id]
        if channelID in expChannel.keys(): newExp *= expChannel[channelID]
        newExp = math.ceil(newExp)

        # Update exp values.
        expData[uid]["msg"] += 1
        expData[uid]["msg-exp"] += newExp
        expData[uid]["exp"] += newExp
    
    elif type == "vc join":
        currentTime = datetime.now()
        timestamp = datetime.isoformat(currentTime)
        expData[uid]["vc-join"] = timestamp

    elif type == "vc leave":
        currentTime = datetime.now()
        joinTimestamp = expData[uid]["vc-join"]

        # Check if join time was saved.
        if joinTimestamp == "":
            await channel.send(f"<@{uid}>\nSowwy, I didn't notice when you joined VC.\nI gave you 25 exp as an apology, please forgive me.")
            expData[uid]["vc-join"] = ""
            expData[uid]["vc-exp"] += 25
            expData[uid]["exp"] += 25
        else:
            # Get minutes since user joined VC.
            joinTime = datetime.fromisoformat(joinTimestamp)
            timeDifference = currentTime - joinTime
            minutes = int(timeDifference.total_seconds() // 60)

            # Calculate new exp to add.
            newExp = expVoice * minutes
            for role in user.roles:
                if role.id in expRole.keys():
                    newExp *= expRole[role.id]
            if channel.id in expChannel.keys(): newExp *= expChannel[channel.id]
            newExp = math.ceil(newExp)

            # Update exp values.
            expData[uid]["vc-join"] = ""
            expData[uid]["vc"] += minutes
            expData[uid]["vc-exp"] += newExp
            expData[uid]["exp"] += newExp
    
    expData = await levelUpdate(user)
    expSave(expData)

# --------------------------------------------------
# -------------------- PROGRAM ---------------------
# --------------------------------------------------

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())


# ---------- ON READY ----------

@bot.event
async def on_ready():
    global serverObj, expData
    serverObj = bot.get_guild(1377373701900865667)

    # Sync slash commands.
    print("Syncing commands...")
    await bot.tree.sync()
    print("\tCommands have been synced.")

    # Check for new server members.
    print("Checking for new members...")
    for member in serverObj.members:
        if str(member.id) not in expData.keys():
            print(f"\tNew member found: {member.name}")
            expData[str(member.id)] = expDefault
    
    expSave(expData)
    print("\tUpdated exp data.")

    # Set bot status.
    print("Setting status...")
    status = random.choice(harmLines)
    await bot.change_presence(
        activity = discord.CustomActivity(name=status),
        status = discord.Status.online
    )
    print(f"\tStatus set to: {status}")

    print(f'Logged in as {bot.user.name}\n')


# ---------- ON MESSAGE ----------

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.channel is None:
        return

    await expUpdate(
        type = "message",
        user = message.author,
        channelID = message.channel.id
    )

    await bot.process_commands(message)


# ---------- ON VC UPDATE ----------

@bot.event
async def on_voice_state_update(user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Check if update is user joining VC.
    if before.channel is None and after.channel is not None:
        await expUpdate(
            type = "vc join",
            user = user,
            channel = after.channel
        )
    # Check if update is user leaving VC.
    elif before.channel is not None and after.channel is None:
        await expUpdate(
            type = "vc leave",
            user = user,
            channel = before.channel
        )


# ---------- ON MEMBER JOIN ----------

@bot.event
async def on_member_join(member: discord.Member):
    global expData

    print(f"\n\nNew member joined: {member.name}")
    expData[str(member.id)] = expDefault
    expSave(expData)


# ---------- RANK ----------

@bot.hybrid_command(name="rank", aliases=["r"])
async def rank(ctx: commands.Context, user: discord.Member = None):
    if user is None: user = ctx.author
    stats = expData[str(user.id)]

    # Add values to message.
    desc = ""
    userLevel = int(stats["lvl"])
    desc += f"Level: **{userLevel}**"
    userExp = int(stats["exp"])
    desc += f"\nTotal exp: **{userExp}**"
    userMessageExp = int(stats["msg-exp"])
    desc += f"\n\nMessage exp: **{userMessageExp}**"
    userVoiceExp = int(stats["vc-exp"])
    desc += f"\nVC exp: **{userVoiceExp}**"
    userMessages = int(stats["msg"])
    desc += f"\n\nTotal messages: **{userMessages}**"
    userVoice = f"{int(stats['vc']//60)}:{int(stats['vc']%60)}"
    desc += f"\nTotal time in VC: **{userVoice}**"

    # Generate embed.
    embed = discord.Embed(
        color = 0x342af9,
        description = desc
    )
    embed.set_author(
        name = user.display_name,
        icon_url = user.display_avatar.url
    )

    await ctx.reply(embed=embed)


# ---------- FORMULA ----------

@bot.hybrid_command(name="formula", aliases=["f", "faggot"])
async def formula(ctx: commands.Context):
    # Add static formulas to message.
    desc = f"exp per message: **{expMessage}**"
    desc += f"\nexp per minute: **{expVoice}**"
    desc += f"\nexp per level (L): **{expFormula[0]} + {expFormula[1]}L^{expFormula[2]}**"

    # Add role multipliers to message.
    desc += "\n\n**ROLE MULTIPLIERS**"
    for id, mult in expRole.items():
        desc += f"\n<@&{id}>: **{mult:.2f}x**"

    # Add channel multipliers to message.
    desc += "\n\n**CHANNEL MULTIPLIERS**"
    for id, mult in expChannel.items():
        desc += f"\n<#{id}>: **{mult:.2f}x**"
    
    # Generate embed.
    embed = discord.Embed(
        color = 0x342af9,
        description = desc
    )
    file = discord.File("assets\levels.png", filename="levels.png")
    embed.set_image(url="attachment://levels.png")

    await ctx.reply(file=file, embed=embed)


# ---------- LEADERBOARD ----------

@bot.hybrid_command(
    name = "leaderboard",
    aliases = ["lb"],
    brief = 'Run "$help leaderboard" to see list of categories.',
    help = "Available categories: main, exp, level, message-exp, voice-exp, messages, voice"
)
async def leaderboard(ctx: commands.Context, category: typing.Literal["main", "exp", "level", "message-exp", "voice-exp", "messages", "voice"] = "main"):
    keys = {
        "main" : "exp",
        "exp" : "exp",
        "level" : "lvl",
        "message-exp" : "msg-exp",
        "voice-exp" : "vc-exp",
        "messages" : "msg",
        "voice" : "vc"
    }

    # Sort users by category.
    key = keys[category]
    results = sorted(
        expData.items(),
        key = lambda item: item[1][key],
        reverse = True
    )
    results = dict(results[:10])
    
    # Add each user to final message.
    desc = ""
    for index, (uid, data) in enumerate(results.items()):
        if category == "main":
            nextLevel = expFormula[0] + ( expFormula[1] * ( (data["lvl"]+1) ** expFormula[2] ) ) # A + Bx^C

            desc += f"\n{index+1}. <@{uid}>"
            desc += f"\n\tLevel: **{data['lvl']}**"
            desc += f"\n\tExp: **{data['exp']}/{nextLevel}**"
        else:
            desc += f"\n{index+1}. <@{uid}>: **{data[key]}**"
    
    # Generate embed.
    embed = discord.Embed(
        color = 0x342af9,
        title = f"Leaderboard for {category}",
        description = desc
    )

    await ctx.reply(embed=embed)


# ---------- TOGGLE REPLY PINGS ----------

@bot.hybrid_command(name="pings")
async def pings(ctx: commands.Context):
    global expData
    uid = str(ctx.author.id)

    if expData[uid]["opt"]["ping"] == 1:
        expData[uid]["opt"]["ping"] = 0
        await ctx.reply(f"Disabled level pings.")
    else:
        expData[uid]["opt"]["ping"] = 1
        await ctx.reply(f"Enabled level pings.")
    
    expSave(expData)

bot.run(os.getenv("TOKEN"))