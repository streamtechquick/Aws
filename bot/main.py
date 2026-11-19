import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import core

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
ADMINS = {
    int(x.strip()) for x in os.getenv("DISCORD_ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def admin(interaction):
    return interaction.user.id in ADMINS

async def reply(interaction, text):
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True)
    else:
        await interaction.response.send_message(text, ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"ARABI VPS Bot online: {client.user}")

@tree.command(name="host", description="Show KVM host status")
async def host(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        data = core.host_info()
        await reply(interaction, "```json\n" + str(data) + "\n```")
    except Exception as e:
        await reply(interaction, f"Host check failed: {e}")

@tree.command(name="vps_list", description="List virtual machines")
async def vps_list(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        await reply(interaction, "```json\n" + str(core.list_vms()) + "\n```")
    except Exception as e:
        await reply(interaction, f"Error: {e}")

@tree.command(name="vps_create", description="Create a VM from an ISO (admin)")
@app_commands.describe(name="VM name", ram_mb="RAM in MB",
                       vcpus="CPU cores", disk_gb="Disk size GB",
                       iso="Absolute ISO path on the KVM host")
async def vps_create(interaction: discord.Interaction, name: str,
                     ram_mb: int, vcpus: int, disk_gb: int, iso: str):
    if not admin(interaction):
        return await reply(interaction, "Admin only.")
    await interaction.response.defer(ephemeral=True)
    try:
        result = core.create_vm(name, ram_mb, vcpus, disk_gb, iso)
        await reply(interaction, f"Created: `{result}`")
    except Exception as e:
        await reply(interaction, f"Create failed: {e}")

async def perform(interaction, name, action):
    if not admin(interaction):
        return await reply(interaction, "Admin only.")
    await interaction.response.defer(ephemeral=True)
    try:
        result = core.vm_action(name, action)
        await reply(interaction, f"`{name}` {action}: {result or 'OK'}")
    except Exception as e:
        await reply(interaction, f"Operation failed: {e}")

@tree.command(name="vps_start", description="Start a VM (admin)")
async def vps_start(interaction: discord.Interaction, name: str):
    await perform(interaction, name, "start")

@tree.command(name="vps_stop", description="Gracefully stop a VM (admin)")
async def vps_stop(interaction: discord.Interaction, name: str):
    await perform(interaction, name, "stop")

@tree.command(name="vps_restart", description="Restart a VM (admin)")
async def vps_restart(interaction: discord.Interaction, name: str):
    await perform(interaction, name, "restart")

@tree.command(name="vps_delete", description="Undefine a VM, preserving its disk (admin)")
async def vps_delete(interaction: discord.Interaction, name: str):
    if not admin(interaction):
        return await reply(interaction, "Admin only.")
    await interaction.response.defer(ephemeral=True)
    try:
        result = core.delete_vm(name)
        await reply(interaction, f"VM `{name}` undefined. Disk was preserved.")
    except Exception as e:
        await reply(interaction, f"Delete failed: {e}")

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is missing. Configure it in .env.")
    client.run(TOKEN)
