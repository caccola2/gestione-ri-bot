import os
import discord
import aiohttp
import sqlite3
from datetime import datetime
from discord.ext import commands
from discord import app_commands, Interaction, Embed, User
from flask import Flask
from threading import Thread

# ──────────────────────────────
# FLASK KEEP-ALIVE
# ──────────────────────────────
app = Flask('')

@app.route('/')
def home():
    return "Bot attivo."

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ──────────────────────────────
# COSTANTI E SETUP BOT
# ──────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ──────────────────────────────
# /ping
# ──────────────────────────────
@bot.tree.command(name="ping", description="Controlla se il bot è attivo")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # in millisecondi
    await interaction.response.send_message(f"✅ Il bot è attivo! Latenza: {latency}ms", ephemeral=True)

# ──────────────────────────────
# AVVIO BOT
# ──────────────────────────────
if __name__ == "__main__":
    token = os.getenv("RI_TOKEN")
    if token:
        bot.run(token)
    else:
        print("[ERRORE] RI_TOKEN mancante.")
