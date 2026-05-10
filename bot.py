import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

EVENTS_CATEGORY_ID = int(os.getenv("EVENTS_CATEGORY_ID"))
PARTIES_CATEGORY_ID = int(os.getenv("PARTIES_CATEGORY_ID"))
STRIKES_CHANNEL_ID = int(os.getenv("STRIKES_CHANNEL_ID"))
WARNINGS_CHANNEL_ID = int(os.getenv("WARNINGS_CHANNEL_ID"))

DATA_FILE = "member_data.json"

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def clean_name(member: discord.Member):
    return member.name.lower().replace(" ", "-")


async def remove_member_assets(guild: discord.Guild, member: discord.Member):
    data = load_data()
    user_data = data.get(str(member.id))

    if not user_data:
        return False

    role = guild.get_role(user_data.get("role_id"))
    channel = guild.get_channel(user_data.get("channel_id"))

    if role and role in member.roles:
        await member.remove_roles(role, reason="Removing member from team")

    if channel:
        await channel.delete(reason=f"Removed private channel for {member}")

    if role:
        await role.delete(reason=f"Removed private role for {member}")

    user_data.pop("role_id", None)
    user_data.pop("channel_id", None)
    data[str(member.id)] = user_data
    save_data(data)

    return True


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")


@app_commands.command(name="addmember", description="Create a private role and channel for a member.")
@app_commands.describe(
    member="The member to add",
    category="Choose events or parties"
)
@app_commands.choices(category=[
    app_commands.Choice(name="Events", value="events"),
    app_commands.Choice(name="Parties", value="parties"),
])
@app_commands.default_permissions(manage_roles=True, manage_channels=True)
async def addmember(interaction: discord.Interaction, member: discord.Member, category: app_commands.Choice[str]):
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)

    category_id = EVENTS_CATEGORY_ID if category.value == "events" else PARTIES_CATEGORY_ID
    category_channel = guild.get_channel(category_id)

    if not category_channel:
        await interaction.followup.send("Category not found. Check your category ID in .env.", ephemeral=True)
        return

    role_name = f"{member.display_name} Team"
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name, reason=f"Added by {interaction.user}")

    await member.add_roles(role, reason=f"Added by {interaction.user}")

    channel_name = clean_name(member)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            read_message_history=True
        )
    }

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category_channel,
        overwrites=overwrites,
        reason=f"Private channel for {member}"
    )

    data = load_data()
    data[str(member.id)] = {
        "role_id": role.id,
        "channel_id": channel.id,
        "strikes": data.get(str(member.id), {}).get("strikes", 0),
        "rpwarnings": data.get(str(member.id), {}).get("rpwarnings", 0)
    }
    save_data(data)

    await interaction.followup.send(
        f"Created role {role.mention} and private channel {channel.mention} for {member.mention}.",
        ephemeral=True
    )


@app_commands.command(name="strike", description="Give a member a strike.")
@app_commands.describe(member="The member to strike", reason="Reason for the strike")
@app_commands.default_permissions(kick_members=True)
async def strike(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.defer(ephemeral=True)

    data = load_data()
    user_data = data.get(str(member.id), {})
    strikes = user_data.get("strikes", 0) + 1
    user_data["strikes"] = strikes
    data[str(member.id)] = user_data
    save_data(data)

    log_channel = interaction.guild.get_channel(STRIKES_CHANNEL_ID)

    try:
        await member.send(
            f"You have received a strike in **{interaction.guild.name}**.\n"
            f"Strike: **{strikes}/2**\n"
            f"Reason: {reason}"
        )
    except discord.Forbidden:
        pass

    if log_channel:
        await log_channel.send(
            f"**Strike issued**\n"
            f"Member: {member.mention}\n"
            f"Strike: **{strikes}/2**\n"
            f"Moderator: {interaction.user.mention}\n"
            f"Reason: {reason}"
        )

    if strikes >= 2:
        await remove_member_assets(interaction.guild, member)
        await interaction.followup.send(
            f"{member.mention} received strike **{strikes}/2** and has been removed from the team.",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"{member.mention} received strike **{strikes}/2**.",
            ephemeral=True
        )


@app_commands.command(name="rpwarning", description="Give a member an RP warning.")
@app_commands.describe(member="The member to warn", reason="Reason for the RP warning")
@app_commands.default_permissions(kick_members=True)
async def rpwarning(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.defer(ephemeral=True)

    data = load_data()
    user_data = data.get(str(member.id), {})
    warnings = user_data.get("rpwarnings", 0) + 1
    user_data["rpwarnings"] = warnings
    data[str(member.id)] = user_data
    save_data(data)

    log_channel = interaction.guild.get_channel(WARNINGS_CHANNEL_ID)

    try:
        await member.send(
            f"You have received an RP warning in **{interaction.guild.name}**.\n"
            f"RP Warning: **{warnings}/3**\n"
            f"Reason: {reason}"
        )
    except discord.Forbidden:
        pass

    if log_channel:
        await log_channel.send(
            f"**RP warning issued**\n"
            f"Member: {member.mention}\n"
            f"RP Warning: **{warnings}/3**\n"
            f"Moderator: {interaction.user.mention}\n"
            f"Reason: {reason}"
        )

    if warnings >= 3:
        await remove_member_assets(interaction.guild, member)
        await interaction.followup.send(
            f"{member.mention} received RP warning **{warnings}/3** and has been removed from the team.",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"{member.mention} received RP warning **{warnings}/3**.",
            ephemeral=True
        )


@app_commands.command(name="removemember", description="Delete a member's private role and channel.")
@app_commands.describe(member="The member to remove")
@app_commands.default_permissions(manage_roles=True, manage_channels=True)
async def removemember(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)

    removed = await remove_member_assets(interaction.guild, member)

    if removed:
        await interaction.followup.send(f"Removed {member.mention}'s role and channel.", ephemeral=True)
    else:
        await interaction.followup.send("No saved role or channel found for that member.", ephemeral=True)


bot.tree.add_command(addmember)
bot.tree.add_command(strike)
bot.tree.add_command(rpwarning)
bot.tree.add_command(removemember)

bot.run(TOKEN)
