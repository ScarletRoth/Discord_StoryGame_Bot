import discord
import random
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View

load_dotenv()

# --- CONFIGURATION INITIALE ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- STATISTIQUES DES CLASSES ---
STATS_DE_BASE = {
    "Guerrier": {"pv": 120, "pv_max": 120, "mana": 0,   "force": 15, "magie": 0},
    "Archer":   {"pv": 90,  "pv_max": 90,  "mana": 20,  "force": 12, "magie": 5},
    "Magicien": {"pv": 60,  "pv_max": 60,  "mana": 100, "force": 3,  "magie": 20},
    "Prêtre":   {"pv": 80,  "pv_max": 80,  "mana": 80,  "force": 5,  "magie": 12}
}

# --- MÉMOIRE DU JEU ---
fiches_perso = {}
ordre_joueurs = []

# --- SYSTÈME DE GLITCH ---
async def repondre_glitch(interaction_ou_ctx, texte):
    """Corrompt le texte aléatoirement avant de l'envoyer."""
    rand = random.random()

    # Scénario 1 : Répétition (15% chance)
    if rand < 0.15:
        texte_glitch = f"{texte} ...{texte}... {texte}"
    # Scénario 2 : Erreur système (10% chance)
    elif rand < 0.25:
        texte_glitch = f"SYSTEM_ALERT : {texte.upper()}"
    # Scénario 3 : Corruption (5% chance)
    elif rand < 0.30:
        texte_glitch = f"N̶o̴n̸.̴.̷.̶ {texte}"
    # Normal (70% chance)
    else:
        texte_glitch = texte

    if hasattr(interaction_ou_ctx, 'response'): 
        if interaction_ou_ctx.response.is_done():
            await interaction_ou_ctx.followup.send(texte_glitch, ephemeral=True)
        else:
            await interaction_ou_ctx.response.send_message(texte_glitch, ephemeral=True)
    else:
        await interaction_ou_ctx.send(texte_glitch)

def get_nom_meta(user_id):
    """Renvoie 'Sujet_Test_X' au lieu du pseudo"""
    if user_id in ordre_joueurs:
        index = ordre_joueurs.index(user_id) + 1
        return f"Sujet_Test_{index}"
    return "Anomalie_Non_Identifiée"

# --- INTERFACE DE CRÉATION ---
class MenuClasse(View):
    def __init__(self):
        super().__init__(timeout=None)

    # 1. GUERRIER
    @discord.ui.button(label="Guerrier", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def bouton_guerrier(self, interaction, button):
        await self.creer_perso(interaction, "Guerrier")

    # 2. ARCHER
    @discord.ui.button(label="Archer", style=discord.ButtonStyle.success, emoji="🏹")
    async def bouton_archer(self, interaction, button):
        await self.creer_perso(interaction, "Archer")

    # 3. MAGICIEN
    @discord.ui.button(label="Magicien", style=discord.ButtonStyle.primary, emoji="🔮")
    async def bouton_mage(self, interaction, button):
        await self.creer_perso(interaction, "Magicien")

    # 4. PRÊTRE
    @discord.ui.button(label="Prêtre", style=discord.ButtonStyle.secondary, emoji="✨")
    async def bouton_pretre(self, interaction, button):
        await self.creer_perso(interaction, "Prêtre")

    # LOGIQUE D'ATTRIBUTION
    async def creer_perso(self, interaction, classe_nom):
        user_id = interaction.user.id
        
        if user_id not in ordre_joueurs:
            ordre_joueurs.append(user_id)

        nouvelles_stats = STATS_DE_BASE[classe_nom].copy()
        nouvelles_stats["classe"] = classe_nom
        fiches_perso[user_id] = nouvelles_stats
        
        nom_meta = get_nom_meta(user_id)
        
        msg = f"Mise à jour du profil pour {nom_meta}. Module '{classe_nom}' installé avec succès."
        await repondre_glitch(interaction, msg)

# --- COMMANDES PRINCIPALES ---
@bot.event
async def on_ready():
    print(f"L'Entité {bot.user} observe...")

@bot.command()
async def creation(ctx):
    """Lance le menu de création"""
    embed = discord.Embed(
        title="CONFIGURATION DES SUJETS",
        description="Sélectionnez un module de combat pour commencer l'expérience.",
        color=0x2f3136
    )
    await ctx.send(embed=embed, view=MenuClasse())

@bot.command()
async def profil(ctx):
    """Affiche la fiche technique du sujet"""
    user_id = ctx.author.id
    nom_meta = get_nom_meta(user_id)

    if user_id in fiches_perso:
        p = fiches_perso[user_id]
        embed = discord.Embed(title=f"Fiche Technique : {nom_meta}", color=0xff0000)
        embed.description = f"**Module :** {p['classe']}"
        embed.add_field(name="Intégrité (PV)", value=f"{p['pv']} / {p['pv_max']}")
        embed.add_field(name="Énergie (Mana)", value=p['mana'])
        embed.add_field(name="Puissance (Force)", value=p['force'])
        embed.add_field(name="Arcane (Magie)", value=p['magie'])
        await ctx.send(embed=embed)
    else:
        await repondre_glitch(ctx, f"Erreur. {nom_meta} n'existe pas dans la base de données.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "aide" in message.content.lower():
        nom_meta = get_nom_meta(message.author.id)
        await repondre_glitch(message.channel, f"Il n'y a pas d'aide pour toi, {nom_meta}.")

    await bot.process_commands(message)

token = os.getenv("TOKEN")
bot.run(token)