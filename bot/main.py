import os
import platform
import subprocess
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ARABI_ADMIN_ID", "0"))

if not TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN secret is missing.")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def is_admin(interaction):
    return interaction.user.id == ADMIN_ID and ADMIN_ID != 0

@client.event
async def on_ready():
    await tree.sync()
    print(f"ARABI VPS BOT ONLINE: {client.user}")

@tree.command(name="host", description="Show ARABI VPS host information")
async def host(interaction: discord.Interaction):
    info = (
        f"Host: {platform.node()}\n"
        f"OS: {platform.platform()}\n"
        f"CPU: {os.cpu_count()}\n"
        f"KVM: {'Available' if os.path.exists('/dev/kvm') else 'Unavailable'}"
    )
    await interaction.response.send_message(info, ephemeral=True)

@tree.command(name="manager", description="Check ARABI VPS Manager")
async def manager(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Administrator only.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "ARABI VPS Manager is installed. Use the Codespace terminal "
        "to manage the host.", ephemeral=True
    )

client.run(TOKEN)
