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

# global data

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

numberEmojis = [[None]*10]*3

# exp data

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
    1433530124934053929 : 0, # chain-chat
    1450201136492711966 : 3  # question-of-the-minty
}

# moc| data

mocDefault = {
    "cases" : [],
    "other" : {}
}

# --------------------------------------------------
# ------------------- LOAD DATA --------------------
# --------------------------------------------------

# Load data from .env file.
load_dotenv()

# Load data from exp.json file.
with open("exp.json") as expFile:
    expData = json.load(expFile)

# Load data from moc|.json file.
with open("moc.json") as mocFile:
    mocData = json.load(mocFile)

# --------------------------------------------------
# ------------------- FUNCTIONS --------------------
# --------------------------------------------------


# ---------- EXP SAVE ----------
# Called when any changes are made to expData.

def expSave(expData: dict):
    with open("exp.json", "w") as expFile:
        json.dump(expData, expFile, indent=4)


# ---------- MOC| SAVE ----------
# Called when any changes are made to mocData.

def mocSave(mocData: dict):
    with open("moc.json", "w") as mocFile:
        json.dump(mocData, mocFile, indent=4)


# ---------- LEVEL UPDATE ----------
# Called when exp is updated, checks if level should also be updated.

async def levelUpdate(user: discord.Member, message: discord.Message = None):
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
        if message is None:
            channel = serverObj.get_channel(1377373703418937477)
            desc = f"{user.display_name} is now level **{currentLevel}**"
            await channel.send(desc)
        else:
            emojis = [
                await bot.fetch_application_emoji(1481376460055904310), # LE
                await bot.fetch_application_emoji(1481376461419057313), # VE
                await bot.fetch_application_emoji(1481376463029800961)  # L
            ]

            # Get number emojis.
            levelText = str(currentLevel)
            for index, number in enumerate(levelText):
                emojis.append(numberEmojis[index][int(number)])
            
            # React with emojis.
            for emoji in emojis:
                await message.add_reaction(emoji)
    
    expData[uid]["lvl"] = currentLevel
    return expData
            

# ---------- EXP UPDATE ----------
# Called whenever a user sends a message, joins a VC, or leaves a VC.

async def expUpdate(
    type: str,
    user: discord.Member,
    channel: discord.VoiceChannel | discord.TextChannel = None,
    message: discord.Message = None
):
    global expData
    uid = str(user.id)

    if type == "message":
        # Calculate new exp to add.
        newExp = expMessage

        # Check for exp roles.
        for role in user.roles:
            if role.id in expRole.keys():
                newExp *= expRole[role.id]
        
        # Check for exp channels.
        if message.channel.type in (discord.ChannelType.public_thread, discord.ChannelType.private_thread):
            channel = message.channel.parent
        else:
            channel = message.channel
        
        if channel.id in expChannel.keys():
            newExp *= expChannel[channel.id]
        
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
            if channel is not None:
                if channel.id in expChannel.keys():
                    newExp *= expChannel[channel.id]
            newExp = math.ceil(newExp)

            # Update exp values.
            expData[uid]["vc-join"] = ""
            expData[uid]["vc"] += minutes
            expData[uid]["vc-exp"] += newExp
            expData[uid]["exp"] += newExp
    
    expData = await levelUpdate(user, message)
    expSave(expData)


# ---------- MOC ACTION ----------
# Called whenever a moc action command is run.

async def mocAction(ctx: commands.Context, actionID: int, reason: str, user: discord.member = None):
    global mocData
    localServerObj = ctx.guild
    localServerID = ctx.guild.id

    actions = [
        ["bwan", "bwanned", "https://cdn.discordapp.com/stickers/1404156262106792047.png?size=512&lossless=true"],
        ["bwarn", "bwarned", "https://media.discordapp.net/stickers/1480600729893994537.webp?size=512&quality=lossless"],
        ["bwute", "bwuted", "https://media.discordapp.net/stickers/1480600818137698414.webp?size=512&quality=lossless"],
        ["bwick", "bwicked", "https://media.discordapp.net/stickers/1480600775100072086.webp?size=512&quality=lossless"]
    ]
    action = actions[actionID]

    # Check if no user is given.
    if user is None:
        if ctx.message.reference is None:
            await ctx.reply("No user given.\nEither reply to someone or mention them as initial argument.")
            return False
        
        referenceID = ctx.message.reference.message_id
        referenceMsg = await ctx.channel.fetch_message(referenceID)
        user = referenceMsg.author

    uid = str(user.id)
    
    # Check if context is given.
    if ctx.message.reference:
        channelID = ctx.message.reference.channel_id
        messageID = ctx.message.reference.message_id
    else:
        channelID = ctx.channel.id
        messageID = ctx.message.id
    
    context = f"https://discord.com/channels/{localServerID}/{channelID}/{messageID}"

    # Create moc| case.
    caseID = mocData["global"]["next-id"]
    mocData[uid]["cases"].append({
        "id" : caseID,
        "type" : action[0],
        "context" : context,
        "reason" : reason
    })
    mocData["global"]["next-id"] += 1

    mocSave(mocData)

    # Create reply embed.
    replyEmbed = discord.Embed(
        color = 0x342af9,
        title = f"{user.name} has been {action[1]}.",
        description = f"**Reason:**\n> {reason}",
        url = context,
    )
    replyEmbed.set_author(
        name = localServerObj.name,
        icon_url = localServerObj.icon.url
    )
    replyEmbed.set_image(
        url = action[2]
    )
    replyEmbed.set_footer(
        text = f"Case #{caseID}; Action done by {ctx.author.name}",
        icon_url = ctx.author.avatar.url
    )

    # Create dm embed.
    dmEmbed = discord.Embed(
        color = 0x342af9,
        title = f"You have been {action[1]}.",
        description = f"**Reason:**\n> {reason}",
        url = context
    )
    dmEmbed.set_author(
        name = localServerObj.name,
        icon_url = localServerObj.icon.url
    )
    dmEmbed.set_image(
        url = action[2]
    )
    dmEmbed.set_footer(
        text = f"Case #{caseID}; Action done by {ctx.author.name}",
        icon_url = ctx.author.avatar.url
    )

    # Send embeds.
    await ctx.reply(embed=replyEmbed)
    await user.send(embed=dmEmbed)

    return True

# --------------------------------------------------
# -------------------- PROGRAM ---------------------
# --------------------------------------------------

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())


# ---------- ON READY ----------

@bot.event
async def on_ready():
    global serverObj, expData, numberEmojis
    serverObj = bot.get_guild(1377373701900865667)

    # Sync slash commands.
    print("Syncing commands...")
    await bot.tree.sync()
    print("\tCommands have been synced.")

    # Create numberEmojis list.
    print("Creating numberEmojis list...")
    for emoji in await bot.fetch_application_emojis():
        emojiName = emoji.name
        if not emojiName.startswith("_"):
            number = int(emojiName[0])
            copy = int(emojiName[1]) - 1

            numberEmojis[copy][number] = emoji
    print("\tCreated numberEmojis list.")

    # Check for new server members.
    print("Checking for new members...")
    for member in serverObj.members:
        uid = str(member.id)

        if uid not in expData.keys():
            print(f"\tNew exp member found: {member.name}")
            expData[uid] = expDefault
        
        if uid not in mocData.keys():
            print(f"\tNew moc| member found: {member.name}")
            mocData[uid] = mocDefault
    
    expSave(expData)
    print("\tUpdated exp data.")

    mocSave(mocData)
    print("\tUpdated moc| data.")
    
    # Check for vc updates.
    print("Checking for vc updates...")

    print("\tChecking for leaves...")
    for uid, userData in expData.items():

        # Check if user was originally in VC.
        if userData["vc-join"] != "":
            user = serverObj.get_member(int(uid))

            # Check if user is still in VC.
            try:
                userVoice = await user.fetch_voice()
                print(f"\t\t{user.display_name} is still in VC.")
            except Exception as bwuu:
                print(f"\t\t{user.display_name} has left VC.")

                # Update exp data.
                await expUpdate(
                    type = "vc leave",
                    user = user,
                    channelID = None
                )
    
    print("\tChecking for joins...")
    for channel in serverObj.voice_channels:
        for user in channel.members:
            uid = str(user.id)

            # Check if user was originally not in VC.
            if expData[uid]["vc-join"] == "":
                print(f"\t\t{user.display_name} is now in VC.")
                await channel.send(f"<@{uid}>\nSowwy, I didn't notice when you joined VC.\nI'll track you from now and I gave you 25 exp as an apology, please forgive me.")

                # Update exp data.
                await expUpdate(
                    type = "vc join",
                    user = user,
                    channelID = channel.id
                )

    # Set bot status.
    print("Setting status...")
    status = random.choice(harmLines)
    await bot.change_presence(
        activity = discord.CustomActivity(name=status),
        status = discord.Status.online
    )
    print(f"\tStatus set to: {status}")

    print(f'Logged in as {bot.user.name}\n')


# ---------- ON ERROR ----------

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(f"The command **{ctx.invoked_with}** does not exist.")
    
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("https://tenor.com/view/noperms-gif-27260516")


# ---------- ON MESSAGE ----------

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.channel is None:
        return

    if message.guild == serverObj:
        await expUpdate(
            type = "message",
            user = message.author,
            message = message
        )

    await bot.process_commands(message)


# ---------- ON MEMBER JOIN ----------

@bot.event
async def on_member_join(member: discord.Member):
    global expData, mocData
    uid = str(member.id)

    if member.guild == serverObj:
        print(f"\n\nNew member joined: {member.name}")

        expData[uid] = expDefault
        expSave(expData)

        mocData[uid] = mocDefault
        mocSave(mocData)


# --------------------------------------------------
# ---------------------- EXP -----------------------
# --------------------------------------------------


# ---------- ON VC UPDATE ----------

@bot.event
async def on_voice_state_update(user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Check if update is user joining VC.
        if before.channel is None and after.channel is not None:
            if after.channel.guild == serverObj:
                await expUpdate(
                    type = "vc join",
                    user = user,
                    channel = after.channel
                )
        # Check if update is user leaving VC.
        elif before.channel is not None and after.channel is None:
            if before.channel.guild == serverObj:
                await expUpdate(
                    type = "vc leave",
                    user = user,
                    channel = before.channel
                )


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


# --------------------------------------------------
# --------------------- OTHER ----------------------
# --------------------------------------------------


# ---------- BWAN USER ----------

@bot.command(name="bwan")
@commands.has_permissions(ban_members = True)
async def bwan(
    ctx: commands.Context,
    user: typing.Optional[discord.Member] = None,
    *, reason: typing.Optional[str] = "No reason given."
):
    actionOutput = await mocAction(
        ctx = ctx,
        actionID = 0,
        reason = reason,
        user = user
    )

    # Check if action is wanted.
    if actionOutput and reason.startswith("// "):
        await user.ban(reason=reason)


# ---------- BWARN USER ----------

@bot.command(name="bwarn")
@commands.has_permissions(kick_members=True)
async def bwarn(
    ctx: commands.Context,
    user: typing.Optional[discord.Member] = None,
    *, reason: typing.Optional[str] = "No reason given."
):
    actionOutput = await mocAction(
        ctx = ctx,
        actionID = 1,
        reason = reason,
        user = user
    )

bot.run(os.getenv("TOKEN"))