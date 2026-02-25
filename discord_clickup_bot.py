import os
import discord
from discord.ext import commands
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")

# Initialize bot with a command prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="task", help="Create a new ClickUp task. Usage: !task <title> | <description>")
async def create_task(ctx, *, args: str):
    """Create a task in ClickUp from a Discord command.

    Args:
        ctx: The context of the command.
        args: The rest of the command after the prefix and name. Use a '|' separator
              to split title and description. Example: !task Fix bug | There is an issue with the API.
    """
    parts = [p.strip() for p in args.split("|", 1)]
    title = parts[0]
    description = parts[1] if len(parts) > 1 else ""

    # Prepare ClickUp API request
    headers = {"Authorization": CLICKUP_API_KEY}
    data = {"name": title, "description": description}
    url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in (200, 201):
        try:
            task_data = response.json()
        except Exception:
            task_data = {}

        # Try to fetch task details from possible keys
        task_id = task_data.get("id") or task_data.get("task", {}).get("id")
        task_name = task_data.get("name") or task_data.get("task", {}).get("name")
        if not task_name:
            task_name = title

        await ctx.send(f"\u2705 Task created: **{task_name}** (ID: {task_id})")
    else:
        await ctx.send(f"\u274c Failed to create task: {response.status_code} {response.text}")

if __name__ == "__main__":
    missing_vars = []
    if not DISCORD_TOKEN:
        missing_vars.append("DISCORD_TOKEN")
    if not CLICKUP_API_KEY:
        missing_vars.append("CLICKUP_API_KEY")
    if not CLICKUP_LIST_ID:
        missing_vars.append("CLICKUP_LIST_ID")

    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
    else:
        bot.run(DISCORD_TOKEN)
