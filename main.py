import os
import discord
import aiohttp
import sqlite3
from datetime import datetime
from discord.ext import commands
from discord import app_commands, Interaction, Embed, User, TextChannel, ForumChannel
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
# EVENTO ON_READY PER SYNC
# ──────────────────────────────
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandi slash sincronizzati: {len(synced)}")
    except Exception as e:
        print(f"❌ Errore nella sincronizzazione dei comandi: {e}")
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="i decreti"))
    print(f"🤖 Bot attivo come {bot.user}")

# ──────────────────────────────
# /ping
# ──────────────────────────────
@tree.command(name="ping", description="Controlla se il bot è attivo")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"✅ Il bot è attivo! Latenza: {latency}ms", ephemeral=True)

# ──────────────────────────────
# /decreto_dpr
# ──────────────────────────────
@tree.command(name="decreto_dpr", description="Pubblica un decreto nel canale e nel forum D.P.R.")
@app_commands.describe(
    nome="Titolo del decreto",
    numero="Numero del decreto (es. 30071/24)",
    link="Link al decreto"
)
async def decreto_dpr(interaction: Interaction, nome: str, numero: str, link: str):
    allowed_roles = [1399830552588189827, 1255957467930558706]
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Non hai i permessi per usare questo comando.", ephemeral=True)

    content = f"""**<:RepubblicaItaliana:1222964737692794961> | {nome}**
*D.P.R. {numero}*

{link}"""

    try:
        guild_text = bot.get_guild(1221870022868078673)
        canale_decreti = guild_text.get_channel(1247648939763830814) if guild_text else None

        if not isinstance(canale_decreti, discord.TextChannel):
            return await interaction.response.send_message("❌ Canale per decreti non trovato o non valido.", ephemeral=True)

        await canale_decreti.send(content)
    except Exception as e:
        return await interaction.response.send_message(f"❌ Errore nell'invio del decreto nel canale: {e}", ephemeral=True)

    try:
        guild_forum = bot.get_guild(1399826720835768461)
        forum = guild_forum.get_channel(1399895001462345759) if guild_forum else None

        if not isinstance(forum, discord.ForumChannel):
            return await interaction.response.send_message("❌ Forum D.P.R. non trovato o non valido.", ephemeral=True)

        tag_dpr = next((tag for tag in forum.available_tags if tag.name.lower() == "d.p.r."), None)
        tags = [tag_dpr] if tag_dpr else []

        await forum.create_thread(
            name=nome,
            content=content,
            applied_tags=tags
        )

    except Exception as e:
        return await interaction.response.send_message(f"❌ Errore nella creazione del post nel forum: {e}", ephemeral=True)

    await interaction.response.send_message("✅ Decreto pubblicato correttamente.", ephemeral=True)

# ──────────────────────────────
# /decreto_dpr
# ──────────────────────────────
@tree.command(name="decreto_gest", description="Pubblica un decreto GEST. nel canale annunci e nel forum.")
@app_commands.describe(
    nome="Titolo del decreto",
    numero="Numero del decreto (es. 30071/24)",
    link="Link al decreto"
)
async def decreto_gest(interaction: Interaction, nome: str, numero: str, link: str):
    allowed_roles = [1399830552588189827, 1255957467930558706]
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Non hai i permessi per usare questo comando.", ephemeral=True)

    content = f"""**<:RepubblicaItaliana:1222964737692794961> | {nome}**
*GEST. {numero}*

{link}"""

    try:
        guild_text = bot.get_guild(1221870022868078673)
        canale_annunci = guild_text.get_channel(1222548780663177276) if guild_text else None

        if not isinstance(canale_annunci, discord.TextChannel):
            return await interaction.response.send_message("❌ Canale annunci non trovato o non valido.", ephemeral=True)

        msg = await canale_annunci.send(content)
        await msg.publish()

    except Exception as e:
        return await interaction.response.send_message(f"❌ Errore nell'invio o pubblicazione del decreto: {e}", ephemeral=True)

    try:
        guild_forum = bot.get_guild(1399826720835768461)
        forum = guild_forum.get_channel(1399895001462345759) if guild_forum else None

        if not isinstance(forum, discord.ForumChannel):
            return await interaction.response.send_message("❌ Forum non trovato o non valido.", ephemeral=True)

        tag_gest = next((tag for tag in forum.available_tags if tag.name.lower() == "gestione r.i."), None)
        tags = [tag_gest] if tag_gest else []

        await forum.create_thread(
            name=nome,
            content=content,
            applied_tags=tags
        )

    except Exception as e:
        return await interaction.response.send_message(f"❌ Errore nella creazione del post nel forum: {e}", ephemeral=True)

    await interaction.response.send_message("✅ Decreto GEST. pubblicato correttamente.", ephemeral=True)

# ──────────────────────────────
# AVVIO BOT
# ──────────────────────────────
if __name__ == "__main__":
    token = os.getenv("RI_TOKEN")
    if token:
        bot.run(token)
    else:
        print("[ERRORE] RI_TOKEN mancante.")
