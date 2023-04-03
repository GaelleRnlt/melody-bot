import discord
import os
import datetime
import random
import asyncio
from pathlib import Path
from boto.s3.connection import S3Connection


env = = S3Connection(os.environ['CHANNEL'], os.environ['TOKEN'])
CHANNEL_ID = env[1] # Récupère l'ID du channel où poster les images depuis les variables d'environnement
IMAGES_DIR = Path(__file__).parent / "Images"  # Le nom du dossier où se trouvent les images

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Bot connecté en tant que {0.user}'.format(client))

    # Lance la tâche de poster une image tous les jours à 12h00
    await client.loop.create_task(post_image_daily())


async def post_image_daily():
    global last_posted_date

    # Attend jusqu'à midi pour poster l'image
    await discord.utils.sleep_until(datetime.datetime.now().replace(hour=12, minute=30, second=0, microsecond=0))


    # Récupère toutes les images commençant par la date actuelle (par exemple, '02_' pour le 2 avril)
    day = datetime.datetime.now().day
    images = [f for f in os.listdir(IMAGES_DIR) if f.startswith(str(day) + "_")]

    if len(images) == 0:
        print("Aucune image trouvée pour aujourd'hui")
        return

    # Choisi une image aléatoire parmi celles trouvées
    image_filename = random.choice(images)

    # Ouvre le fichier image en mode binaire pour le charger dans un objet discord.File
    with open(os.path.join(IMAGES_DIR, image_filename), 'rb') as f:
        image_file = discord.File(f)

    # Supprime le dernier message posté dans le channel
    channel = client.get_channel(int(CHANNEL_ID))
    async for message in channel.history(limit=1):
        await message.delete()

    # Poste l'image dans le channel
    await channel.send(file=image_file)


    # Met le bot en veille jusqu'à demain
    await asyncio.sleep(86400)
    # Redémarre le script Python
    os.execl(sys.executable, sys.executable, *sys.argv)


client.run(env[2])
