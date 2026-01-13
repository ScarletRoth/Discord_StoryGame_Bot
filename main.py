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
inventaires = {}
progression = {}

# --- SYSTÈME DE GLITCH ---
async def repondre_glitch(interaction_ou_ctx, texte):
    """Corrompt le texte aléatoirement avant de l'envoyer."""
    rand = random.random()

    if rand < 0.15:
        texte_glitch = f"{texte} ...{texte}... {texte}"
    elif rand < 0.25:
        texte_glitch = f"SYSTEM_ALERT : {texte.upper()}"
    elif rand < 0.30:
        texte_glitch = f"N̶o̴n̸.̴.̷.̶ {texte}"
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

    contenu = message.content.lower()
    user_id = message.author.id
    
    salle_actuelle = progression.get(user_id, 0)
    
    classe_joueur = "Inconnu"
    if user_id in fiches_perso:
        classe_joueur = fiches_perso[user_id]["classe"]

    # --- SALLE 1 : LA CELLULE ---
    if salle_actuelle == 1 or salle_actuelle == 0:
        if "fouille" in contenu or "regarde" in contenu:
            chance = random.randint(1, 20)
            if chance > 10:
                if user_id not in inventaires or "Clef" not in inventaires[user_id]:
                    ajouter_objet(user_id, "Clef")
                    progression[user_id] = 1 
                    await repondre_glitch(message.channel, "Tu trouves une **Clef** caché dans la paille.")
                else:
                    await message.channel.send("Tu as déjà la clef.")
            else:
                await message.channel.send("Rien ici.")
        
        elif "ouvre" in contenu and "porte" in contenu:
            if user_id in inventaires and "Clef" in inventaires[user_id]:
                await message.add_reaction("🗝️")
                await message.reply("La porte s'ouvre ! Tape `!enigme2` pour avancer.")
            else:
                await message.reply("La porte est fermée.")

    # --- SALLE 2 : LE COULOIR ---
    elif salle_actuelle == 2:
        if "attaque" in contenu or "frapper" in contenu or "taper" in contenu:
            if classe_joueur in ["Guerrier", "Archer"]:
                await repondre_glitch(message.channel, f"{classe_joueur} en action ! Tu brises les os du squelette en un coup critique.\nLe passage est libre.")
                progression[user_id] = 3
            elif classe_joueur in ["Magicien", "Prêtre"]:
                await repondre_glitch(message.channel, "Tu tapes le squelette avec ton bâton... Il rigole (bruitage manquant). Ça ne marche pas, tu n'es pas assez fort physiquement.")
            else:
                await message.reply("Tu essaies de te battre à mains nues ? Mauvaise idée.")

        elif "sort" in contenu or "magie" in contenu or "prier" in contenu or "feu" in contenu:
            if classe_joueur in ["Magicien", "Prêtre"]:
                await repondre_glitch(message.channel, f"Une lumière aveuglante jaillit de tes mains ! Le squelette tombe en poussière.\nLe passage est libre.")
                progression[user_id] = 3
            else:
                await message.reply("Tu agites les bras en criant 'Abracadabra'... Le squelette te regarde, confus. Tu n'es pas magicien.")

        elif "parle" in contenu or "bonjour" in contenu:
             await repondre_glitch(message.channel, "Le squelette répond : 'E̷r̷r̷o̷r̷ 404: Dialogue not found'. Il t'attaque !")

    await bot.process_commands(message)

@bot.command()
async def roll(ctx):
    """Lance un dé de 20 faces... théoriquement."""
    user_id = ctx.author.id
    nom_meta = get_nom_meta(user_id)
    
    resultat = random.randint(1, 20)
    
    rand_glitch = random.random()
    
    msg = ""

    if rand_glitch < 0.10:
        resultat = 1
        msg = f"🎲 {nom_meta} lance le dé... **{resultat}**. (Échec Critique forcée par le système)"
        
    elif rand_glitch < 0.15:
        resultat_impossible = random.choice([-5, 21, 404, 0, "NULL"])
        msg = f"🎲 {nom_meta} lance le dé... Résultat : **{resultat_impossible}**. \n ERROR : Valeur hors limites."
        
    elif resultat < 5:
        msg = f"🎲 {nom_meta} a fait **{resultat}**. Pathétique."
        
    else:
        msg = f"🎲 {nom_meta} a obtenu **{resultat}** / 20."

    await repondre_glitch(ctx, msg)

@bot.command()
async def sac(ctx):
    """Affiche l'inventaire du joueur"""
    user_id = ctx.author.id
    nom_meta = get_nom_meta(user_id)
    
    if user_id not in inventaires or len(inventaires[user_id]) == 0:
        await repondre_glitch(ctx, f"L'inventaire de {nom_meta} est vide. Comme son existence.")
    else:
        liste_objets = "\n- ".join(inventaires[user_id])
        embed = discord.Embed(title=f"Sac de {nom_meta}", description=f"- {liste_objets}", color=0x9b59b6)
        await ctx.send(embed=embed)

def ajouter_objet(user_id, objet):
    """Fonction utilitaire pour donner un objet"""
    if user_id not in inventaires:
        inventaires[user_id] = []
    inventaires[user_id].append(objet)

@bot.command()
async def enigme1(ctx):
    """Lance la première scène : Le Cachot."""

    await repondre_glitch(ctx, "Chargement du niveau : DONJON_OBSCUR...")

    embed = discord.Embed(
        title="CHAPITRE 1 : La Geôle Oubliée",
        description=(
            "Vous ouvrez les yeux dans une cellule sombre et humide. "
            "L'air sent le moisi et la pierre froide.\n\n"
            "Devant vous se dresse une lourde **porte** en bois renforcée de fer. Elle n'a pas de serrure apparente.\n"
            "Dans le coin de la pièce, un tas de **paille** pourrie semble avoir servi de lit.\n\n"
            "*Que faites-vous ?*"
        ),
        color=0x8B4513
    )
    progression[ctx.author.id] = 1
    
    embed.set_footer(text="Indice : Interagissez avec les éléments en gras.")
    await ctx.send(embed=embed)

@bot.command()
async def enigme2(ctx):
    """Lance la scène 2 : Le Garde Squelette."""
    user_id = ctx.author.id
    
    if user_id not in inventaires or "Clef" not in inventaires[user_id]:
        await repondre_glitch(ctx, "Triche détectée. Vous n'avez pas ouvert la porte précédente.")
        return

    progression[user_id] = 2
    
    await repondre_glitch(ctx, "Chargement de l'entité hostile... Modèle : SKELETON_WARRIOR_LVL1.")

    embed = discord.Embed(
        title="CHAPITRE 2 : Le Couloir des Ombres",
        description=(
            "Vous débouchez dans un long couloir éclairé par des torches vacillantes.\n"
            "Au milieu du passage, un **Squelette** en armure rouillée monte la garde. Il tient une épée rouillée.\n\n"
            "Il tourne son crâne vide vers vous. Ses yeux brillent d'une lueur rouge (bug graphique probable).\n\n"
            "*Il va falloir se battre ou ruser...*"
        ),
        color=0x000000
    )
    embed.set_footer(text="Actions suggérées : Attaquer, Lancer un sort, Discuter...")
    await ctx.send(embed=embed)

token = os.getenv("TOKEN")
bot.run(token)