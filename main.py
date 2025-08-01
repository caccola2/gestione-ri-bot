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
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
GROUP_ID = 9927486
PERMESSI_AUTORIZZATI = [1226305676708679740, 1244221458096455730]

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ──────────────────────────────
# DATABASE SQLITE
# ──────────────────────────────
conn = sqlite3.connect("porto_armi.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS esiti_porto_armi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nome_roblox TEXT NOT NULL,
    esito TEXT NOT NULL,
    nome_funzionario TEXT NOT NULL,
    data_emissione TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS licenze_porto_armi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_roblox TEXT NOT NULL,
    data_rilascio TEXT NOT NULL,
    nome_funzionario TEXT NOT NULL,
    note TEXT
)
""")

conn.commit()

# ──────────────────────────────
# UTILITY
# ──────────────────────────────
def ha_permessi(member):
    return any(role.id in PERMESSI_AUTORIZZATI for role in member.roles)

async def get_user_id(session, username):
    url = "https://users.roblox.com/v1/usernames/users"
    async with session.post(url, json={"usernames": [username], "excludeBannedUsers": False}) as resp:
        data = await resp.json()
        return data["data"][0]["id"] if data.get("data") else None

async def get_csrf_token(session):
    async with session.post("https://auth.roblox.com/v2/logout") as resp:
        return resp.headers.get("x-csrf-token")

# ──────────────────────────────
# EVENTO READY
# ──────────────────────────────
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot pronto. Comandi sincronizzati: {len(synced)}")
    except Exception as e:
        print(f"[ERRORE SYNC]: {e}")

# ──────────────────────────────
# TEMPORANEO IMPORT LICENZE
# ──────────────────────────────

@tree.command(name="importa_licenze_massive", description="⚠️ Importa in blocco licenze. SOLO PER USO TEMPORANEO.")
async def importa_licenze_massive(interaction: discord.Interaction):
    # Sostituisci con il tuo ID Discord per sicurezza
    if interaction.user.id != 934162644821241907:
        return await interaction.response.send_message("❌ Non hai il permesso di usare questo comando.", ephemeral=True)

    # Lista dati da importare (nome_roblox, funzionario, data)
    licenze_massive = [
        ("jretyyyh", "Ministero dell'Interno", "04/05/2025"),
        ("franci53", "Ministero dell'Interno", "04/05/2025"),
        ("antonioilprobello", "Ministero dell'Interno", "02/11/2024"),
        ("carabiniere0902", "Ministero dell'Interno", "02/11/2024"),
        ("Den_910ce", "Ministero dell'Interno", "02/11/2024"),
        ("antoxx_20", "antonioilprobello", ""),
        ("XZMANUL", "Ministero dell'Interno", "02/11/2024"),
        ("777reac7or", "xzmanul", "28/04/2025"),
        ("supercaccola2", "Ministero dell'Interno", "21/07/2025"),
        ("ammiragli", "Ministero dell'Interno", "02/11/2024"),
        ("VainVerrater", "Ministero dell'Interno", "02/01/2025"),
        ("jmicco", "Ministero dell'Interno", "22/04/2025"),
        ("nicoscarza", "antonioilprobello", "22/04/2025"),
        ("savagekotek", "antonioilprobello", "22/04/2025"),
        ("leonardoviviani", "antonioilprobello", "22/04/2025"),
        ("D3M0N_910", "antonioilprobello", "22/04/2025"),
        ("Aversa_Cristian2", "antonioilprobello", "22/04/2025"),
        ("CovetingCape", "antonioilprobello", "22/04/2025"),
        ("Willyz_00", "antonioilprobello", "22/04/2025"),
        ("Mattia_1930", "antonioilprobello", "22/04/2025"),
        ("Kalito_Singel", "antonioilprobello", "22/04/2025"),
        ("Costa1090", "xzmanul", "28/04/2025"),
        ("diegn100", "xzmanul", "28/04/2025"),
        ("peppos_11", "xzmanul", "28/04/2025"),
        ("verowgf21s", "antonioilprobello", "02/05/2025"),
        ("Thefili02", "Zenyon00", "21/05/2025"),
        ("Harlock_099", "Zenyon00", "21/05/2025"),
        ("RangoBoy003", "D3MON_910", "01/06/2025"),
        ("ITS_FLAMEH12", "D3M0N_910", "09/06/2025"),
        ("gius_valls", "Mattia_1930", "04/07/2025"),
        ("alex_tvb12", "Mattia_1930", "04/07/2025"),
        ("UnreelevantCrazy", "Mattia_1930", "04/07/2025"),
        ("vdygf41", "Mattia_1930", "04/07/2025"),
        ("ema_104104", "supercaccola2", "09/06/2025"),
        ("itzmimmo", "supercaccola2", "05/07/2025"),
        ("RS_RomaStarYT", "Mattia_1930", "06/07/2025"),
        ("FortAndrea124", "Mattia_1930", "07/06/2025"),
        ("demonePOLLO2389", "Zenyon00", "29/05/2025"),
        ("domgod4242", "supercaccola2", "08/07/2025"),
        ("Gabrieledybala10", "supercaccola2", "08/07/2025"),
        ("0FRANCESCO_COZZUPOLI", "supercaccola2", "08/07/2025"),
        ("ssyyudyrx", "supercaccola2", "08/07/2025"),
        ("CiccioDonnaRumma", "supercaccola2", "08/07/2025"),
        ("Doge542233", "supercaccola2", "08/07/2025"),
        ("Ragnozeo08", "supercaccola2", "08/07/2025"),
        ("Tavixyt7", "D3M0N_910", "10/07/2025"),
        ("giorgio_real2", "supercaccola2", "08/07/2025"),
        ("vigilante2356", "Mattia_1930", "13/07/2025"),
        ("Krisuzzo", "supercaccola2", "13/07/2025"),
        ("Fabio_123403", "supercaccola2", "13/07/2025"),
        ("Quac_26", "Mattia_1930", "14/07/2025"),
        ("utenteog", "supercaccola2", "17/07/2025"),
        ("PixelDrago_52", "supercaccola2", "19/07/2025"),
        ("GIANLUONFIRE", "supercaccola2", "20/07/2025"),
        ("blurm324234", "supercaccola2", "20/07/2025"),
        ("Gamefr555", "supercaccola2", "20/07/2025"),
        ("JstBarlox", "supercaccola2", "20/07/2025"),
    ]

    conn = sqlite3.connect("porto_armi.db")
    c = conn.cursor()
    count = 0

    for nome_roblox, funzionario, data in licenze_massive:
        c.execute("SELECT * FROM licenze_porto_armi WHERE nome_roblox = ?", (nome_roblox,))
        if c.fetchone() is None:
            c.execute("INSERT INTO licenze_porto_armi (nome_roblox, data_rilascio, nome_funzionario, note) VALUES (?, ?, ?, ?)",
                      (nome_roblox, data, funzionario, "Importazione massiva"))
            count += 1

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"✅ Importate {count} licenze nel database.", ephemeral=True)


# ──────────────────────────────
# COMANDI PORTO D'ARMI
# ──────────────────────────────
@tree.command(name="esito-porto-armi", description="Invia esito porto d'armi in DM e registra")
@app_commands.describe(destinatario="Utente a cui inviare l'esito", nome_funzionario="Nome del funzionario", esito="Esito (ACCOGLIE o RIGETTA)", nome_richiedente="Nome del richiedente (Roblox)", data_emissione="Data (GG/MM/AAAA)")
async def esito_porto_armi(interaction: Interaction, destinatario: User, nome_funzionario: str, esito: str, nome_richiedente: str, data_emissione: str):
    esito = esito.upper()
    if esito not in ["ACCOGLIE", "RIGETTA"]:
        return await interaction.response.send_message("❌ Esito non valido.", ephemeral=True)

    embed = Embed(title="ESITO RICHIESTA PORTO D'ARMA", color=0x2b2d31, description=(
        "**VISTO** il regolamento sul rilascio del porto d'armi emesso in data 02/06/2024\n"
        "**VISTO** l'articolo 27 del testo unico delle leggi di pubblica sicurezza\n\n"
        f"Il funzionario **{nome_funzionario}**\n\n"
        f"**{esito}**\n\n"
        f"La richiesta per il porto d'armi del sig. **{nome_richiedente}**.\n\n"
        f"Lì, d'ufficio, il funzionario **{nome_funzionario}**\n"
        f"**{data_emissione}**"
    ))
    embed.set_footer(text="Sistema di Comunicazioni Dirette – Ministero dell'Interno", icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None)

    try:
        await destinatario.send(embed=embed)
        cursor.execute("INSERT INTO esiti_porto_armi (user_id, nome_roblox, esito, nome_funzionario, data_emissione) VALUES (?, ?, ?, ?, ?)",
                       (destinatario.id, nome_richiedente, esito, nome_funzionario, data_emissione))
        conn.commit()
        await interaction.response.send_message(f"✅ Esito inviato a {destinatario.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Impossibile inviare DM.", ephemeral=True)

@tree.command(name="registra-licenza", description="Registra una licenza di porto d'armi")
@app_commands.describe(nome_roblox="Nome utente Roblox", nome_funzionario="Funzionario che rilascia", data_rilascio="Data rilascio", note="Note aggiuntive (opzionale)")
async def registra_licenza(interaction: Interaction, nome_roblox: str, nome_funzionario: str, data_rilascio: str, note: str = "Nessuna"):
    cursor.execute("INSERT INTO licenze_porto_armi (nome_roblox, data_rilascio, nome_funzionario, note) VALUES (?, ?, ?, ?)",
                   (nome_roblox, data_rilascio, nome_funzionario, note))
    conn.commit()
    await interaction.response.send_message(f"✅ Licenza registrata per **{nome_roblox}**.", ephemeral=True)

@tree.command(name="elimina-soggetto", description="Elimina un soggetto dal database")
@app_commands.describe(nome_roblox="Nome utente Roblox")
async def elimina_soggetto(interaction: Interaction, nome_roblox: str):
    cursor.execute("DELETE FROM licenze_porto_armi WHERE nome_roblox = ?", (nome_roblox,))
    cursor.execute("DELETE FROM esiti_porto_armi WHERE nome_roblox = ?", (nome_roblox,))
    conn.commit()
    await interaction.response.send_message(f"🗑️ **{nome_roblox}** eliminato.", ephemeral=True)

@tree.command(name="cerca-soggetto", description="Cerca un soggetto nel database")
@app_commands.describe(nome_roblox="Nome utente Roblox")
async def cerca_soggetto(interaction: Interaction, nome_roblox: str):
    cursor.execute("SELECT * FROM licenze_porto_armi WHERE nome_roblox = ?", (nome_roblox,))
    licenza = cursor.fetchone()

    cursor.execute("SELECT * FROM esiti_porto_armi WHERE nome_roblox = ?", (nome_roblox,))
    esito = cursor.fetchone()

    if not licenza and not esito:
        return await interaction.response.send_message("❌ Nessun dato trovato.", ephemeral=True)

    embed = Embed(title=f"📄 Dati per {nome_roblox}", color=0x5865F2)
    if licenza:
        embed.add_field(name="Licenza", value=f"Rilasciata il: {licenza[2]}\nFunzionario: {licenza[3]}\nNote: {licenza[4]}", inline=False)
    if esito:
        embed.add_field(name="📩 Ultimo Esito", value=f"Esito: {esito[3]}\nFunzionario: {esito[4]}\nData: {esito[5]}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="lista-licenze", description="Mostra tutte le licenze registrate")
async def lista_licenze(interaction: Interaction):
    cursor.execute("SELECT nome_roblox, data_rilascio FROM licenze_porto_armi")
    risultati = cursor.fetchall()
    if not risultati:
        return await interaction.response.send_message("⚠️ Nessuna licenza trovata.", ephemeral=True)
    descrizione = "\n".join([f"• {nome} – {data}" for nome, data in risultati])
    embed = Embed(title="📜 Lista Licenze Porto d'Armi", description=descrizione, color=0x00ff00)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ──────────────────────────────
# COMANDO ESITO GPG
# ──────────────────────────────
@tree.command(name="esito-gpg", description="Invia esito GPG in DM")
@app_commands.describe(destinatario="Utente", esito="Esito", note="Note opzionali")
async def esito_gpg(interaction: Interaction, destinatario: User, esito: str, note: str = "Nessuna"):
    embed = Embed(title="ESITO GPG", description=f"**Esito:** {esito}\n**Note:** {note}", color=0xffcc00)
    try:
        await destinatario.send(embed=embed)
        await interaction.response.send_message("✅ Esito GPG inviato.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ DM bloccati.", ephemeral=True)

# ──────────────────────────────
# COMANDO GRUPPO ROBLOX
# ──────────────────────────────
@tree.command(name="kick_group", description="Espelle un utente dal gruppo")
@app_commands.describe(username="Username Roblox")
async def kick_group(interaction: Interaction, username: str):
    if not ha_permessi(interaction.user):
        return await interaction.response.send_message("❌ Permessi insufficienti.", ephemeral=True)
    async with aiohttp.ClientSession() as session:
        user_id = await get_user_id(session, username)
        if not user_id:
            return await interaction.response.send_message("❌ Utente non trovato.", ephemeral=True)
        token = await get_csrf_token(session)
        headers = {"Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}", "x-csrf-token": token}
        async with session.post(f"https://groups.roblox.com/v1/groups/{GROUP_ID}/users/{user_id}", headers=headers) as resp:
            if resp.status == 200:
                await interaction.response.send_message(f"✅ {username} espulso dal gruppo.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Errore durante l'espulsione.", ephemeral=True)

# ──────────────────────────────
# AVVIO BOT
# ──────────────────────────────
if __name__ == "__main__":
    token = os.getenv("MINISTERO_TOKEN")
    if token:
        bot.run(token)
    else:
        print("[ERRORE] MINISTERO_TOKEN mancante.")
