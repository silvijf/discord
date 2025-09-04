import discord
from discord import app_commands
from discord.ext import commands
import os
import dotenv
import asyncio
import time
from typing import Optional
import replit
import requests
import math
import random as r

dotenv.load_dotenv()

autoreplier = False

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f'Bot is online als {bot.user}')
    await tree.sync()

@bot.command()
async def ping(ctx):
    print("We spelen ping pong!")
    await ctx.send("Pong!")

@bot.command()
async def schiet(ctx):
    print("Pang!")
    await ctx.send("Pang! :gun:")

@bot.command()
async def random(ctx):
    random_number = r.randrange(0, 10)
    print(f"Het nummer is {random_number}")
    await ctx.send(f"{random_number}!")

@bot.event
async def on_message(msg):
    global autoreplier, autoreply_text
    if not msg.author.bot and autoreplier and msg.channel == autoreply_channel:
        print("Autoreply uit.")
        await autoreply_channel.send(autoreply_text)
        autoreplier = False
    await bot.process_commands(msg)

@tree.command(name="autoreply", description="Antwoordt meteen als iemand iets zegt")
@app_commands.describe(text="Wat moet de bot zeggen?")
async def autoreply(interaction: discord.Interaction, text: str):
    print("Autoreply aan.")
    global autoreplier
    global autoreply_text
    global autoreply_channel
    autoreplier = True
    autoreply_text = text
    autoreply_channel = interaction.channel
    await interaction.response.send_message(f'Autoreply is geactiveerd met tekst: "{text}"!', ephemeral=True)


@tree.command(name="say", description="Zegt iets")
@app_commands.describe(text="Wat moet de bot zeggen?",
                       erm_actually='Moet de bot "Erm actually ☝️🤓" zeggen?',
                       time="Hoe lang moet het duren voordat de bot dit zegt? (in seconden)",
                       message_id="Waarop moet de bot reageren? Geef een Message ID.")
async def say(interaction: discord.Interaction, text: str, erm_actually: Optional[bool] = False, time: Optional[int] = None, message_id: Optional[str] = None):
    print(f"Nou, {text}")
    await interaction.response.defer()
    try:
        if time:
            await asyncio.sleep(time)
    except:
        pass
    channel = interaction.channel
    if message_id:
        try:
            message_id = message_id.split("-")[1]
        except:
            pass
        msg = await channel.fetch_message(int(message_id))
        await msg.reply(text)
    else:
        if erm_actually:
            await channel.send(f"Erm actually ☝️🤓 {text}")
        else:
            await channel.send(text)

Vars = {}
var_group = app_commands.Group(name="var", description="Commands met variabelen.")
async def name_vars(interaction):
    text = "## Variabelen:\n"
    print(Vars)
    if Vars:
        for i in range(len(Vars)):
            text += f"**{list(Vars.keys())[i]}**: {list(Vars.values())[i]}\n"
        try:
            await interaction.response.send_message(text)
        except:
            await interaction.channel.send(text)
    else:
        try:
            await interaction.response.send_message("Geen variabelen.")
        except:
            await interaction.channel.send("Geen variabelen.")

@var_group.command(name="set", description="Onthoudt een getal.")
@app_commands.describe(key="Wat moet de key zijn naar de variabele?", value="Wat moet de value zijn?")
async def var_set(interaction: discord.Interaction, key: str, value: int):
    Vars[key] = value
    author = interaction.user.mention
    text = f"{author} maakte {key} {value}!"
    await interaction.response.send_message(text)
    await name_vars(interaction)

@var_group.command(name="delete", description="Verwijdert een variabele.")
@app_commands.describe(key="Wat is de key naar de variabele?")
async def var_set(interaction: discord.Interaction, key: str):
    Vars.pop(key)
    author = interaction.user.mention
    text = f"{author} verwijderde {key}!"
    await interaction.response.send_message(text)
    await name_vars(interaction)

@var_group.command(name="add", description="Telt een getal op bij je variabele.")
@app_commands.describe(key="Wat is de key naar de variabele?", value="Hoeveel moet erbij opgeteld worden?")
async def var_add(interaction: discord.Interaction, key: str, value: int):
    try:
        Vars[key] += value
        author = interaction.user.mention
        text = f"{author} voegde {value} toe aan {key}!"
        await interaction.response.send_message(text)
        await name_vars(interaction)
    except:
        await interaction.response.send_message("Die variabele bestaat niet (meer).")
@var_group.command(name="subtract", description="Trekt een getal af van je variabele.")
@app_commands.describe(key="Wat is de key naar de variabele?", value="Hoeveel moet ervan afgetrokken worden?")
async def var_subtract(interaction: discord.Interaction, key: str, value: int):
    try:
        Vars[key] -= value
        author = interaction.user.mention
        text = f"{author} trok {value} af van {key}!"
        await interaction.response.send_message(text)
        await name_vars(interaction)
    except:
        await interaction.response.send_message("Die variabele bestaat niet (meer).")

@var_group.command(name="view", description="Bekijk je variabelen")
async def vars_view(interaction: discord.Interaction):
    await name_vars(interaction)

tree.add_command(var_group)


class PlatformerView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.x = 0
        self.y = 2
        self.x2 = 0
        self.y2 = 2
        self.platforms = [[3, 2], [4, 1], [6, 0]]
        self.jumping = False
        self.jumping2 = False
        self.p1 = interaction.user
        self.p2 = None

    async def move(self, interaction):
        text = ""
        for line in range(3):
            for i in range(6):
                if i == self.x and i == self.x2 and line == self.y & line == self.y2:
                    text += "🟨"
                elif i == self.x and line == self.y:
                    text += "🟩"
                elif i == self.x2 and line == self.y2:
                    text += "🟥"
                elif [i, line] in self.platforms:
                    text += "⬛"
                else:
                    text += "🟦"
            text += "\n"
        await interaction.message.edit(content=text, view=self)
        try:
            await interaction.response.defer()
        except:
            pass
        if self.y < 2 and [self.x, self.y + 1] not in self.platforms:
            self.jumping = True
            await asyncio.sleep(1)
            if self.y < 2 and [self.x, self.y + 1] not in self.platforms:
                self.y += 1
                await self.move(interaction)
        else:
            self.jumping = False
        if self.y2 < 2 and [self.x2, self.y2 + 1] not in self.platforms:
            self.jumping2 = True
            await asyncio.sleep(1)
            if self.y2 < 2 and [self.x2, self.y2 + 1] not in self.platforms:
                self.y2 += 1
                await self.move(interaction)
        else:
            self.jumping2 = False

    @discord.ui.button(label=chr(8592), style=discord.ButtonStyle.primary)
    async def button_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.p1:
            if self.x > 0 and [self.x - 1, self.y] not in self.platforms:
                self.x -= 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)    
        elif interaction.user == self.p2:
            if self.x2 > 0 and [self.x2 - 1, self.y2] not in self.platforms:
                self.x2 -= 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
        elif not self.p2:
            self.p2 = interaction.user
            self.x2 -= 1
        else:
            await interaction.response.send_message("Je doet hier niet aan mee. Start een nieuw spel!", ephemeral=True)
        await self.move(interaction)
        
    @discord.ui.button(label=chr(8593), style=discord.ButtonStyle.primary)
    async def button_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.p1:
            if self.y > 0 and [self.x, self.y - 1] not in self.platforms and not self.jumping:
                self.y -= 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)    
        elif interaction.user == self.p2:
            if self.y2 > 0 and [self.x2, self.y2 - 1] not in self.platforms and not self.jumping2:
                self.y2 -= 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
        elif not self.p2:
            self.p2 = interaction.user
            self.y2 -= 1
        else:
            await interaction.response.send_message("Je doet hier niet aan mee. Start een nieuw spel!", ephemeral=True)


        await self.move(interaction)
        await asyncio.sleep(1)
        
    @discord.ui.button(label=chr(8594), style=discord.ButtonStyle.primary)
    async def button_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.p1:
            if self.x < 5 and [self.x + 1, self.y] not in self.platforms:
                self.x += 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)    
        elif interaction.user == self.p2:
            if self.x2 < 5 and [self.x2 + 1, self.y2] not in self.platforms:
                self.x2 += 1
            else:
                await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
        elif not self.p2:
            self.p2 = interaction.user
            self.x2 += 1
        else:
            await interaction.response.send_message("Je doet hier niet aan mee. Start een nieuw spel!", ephemeral=True)
        
        await self.move(interaction)
    

@tree.command(name="platformer", description="Platformer game!")
async def platformer(interaction: discord.Interaction):
    print("Platformer executed!")
    view = PlatformerView(interaction)
    await interaction.channel.send("🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦⬛🟦\n🟨🟦🟦⬛🟦🟦", view=view)

class HomeView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.user = interaction.user
        self.obstacles = [[4, 3], [5, 3]]
        self.ogobsnames = ["couch_left", "couch_right"]
        self.couch = [4, 3]
        try:
            self.coins = replit.db[str(interaction.user.id)]["coins"]
            self.x = replit.db[str(interaction.user.id)]["x"]
            self.y = replit.db[str(interaction.user.id)]["y"]
            self.obstaclenames = list(replit.db[str(interaction.user.id)]["obstaclenames"])
            if replit.db[str(interaction.user.id)]["day"] == math.floor(time.time() / 86400):
                self.sat = replit.db[str(interaction.user.id)]["sat"]
            else:
                self.sat = False
                replit.db[str(interaction.user.id)]["sat"] = False
            self.time = replit.db[str(interaction.user.id)]["time"]
        except:
            replit.db[str(interaction.user.id)] = {}
            self.coins = 0
            replit.db[str(interaction.user.id)]["coins"] = 0
            self.x = 5
            self.y = 2
            self.obstaclenames = ["couch_left", "couch_right"]
            self.day =  math.floor(time.time() / 86400)
            replit.db[str(interaction.user.id)]["day"] = self.day
            self.time = None
            self.sat = False
        replit.db[str(interaction.user.id)]["day"] = math.floor(time.time() / 86400)
        self.canmove = False
    
    async def move(self, interaction):
        self.canmove = True
        replit.db[str(interaction.user.id)]["coins"] = self.coins
        try:
            await interaction.response.defer()
        except:
            pass
        text = f"## 🪙 {self.coins}\nDit is je huis!\n"
        for item in self.children:
            if item.custom_id == "use":
                if [self.x, self.y - 1] in self.obstacles or self.obstaclenames != self.ogobsnames:
                    item.disabled = False
                    await interaction.message.edit(content=text, view=self)
                else:
                    item.disabled = True
            if self.obstaclenames != self.ogobsnames:
                if isinstance(item, discord.ui.Button) and item.custom_id != "use":
                    item.disabled = True
            else:
                if isinstance(item, discord.ui.Button) and item.custom_id != "use":
                    item.disabled = False
        
        if self.obstaclenames != self.ogobsnames and self.time:
            text += "Coins die je krijgt als je van de bank af gaat (hangt af van hoe lang je zit):\n"
            if not self.sat:
                if math.floor((time.time() / 120 - self.time / 120)) <= 30:
                    text += f"### 🪙 {str(math.floor((time.time() / 120 - self.time / 120)))}\n"
                    text += "Onthoud, als je langer dan een uur zit gaan alle coins weg!\n"
                else:
                    text += "Alle coins zijn weg, want je zit al langer dan een uur...\n"
            else:
                text += "Je hebt vandaag al gezeten! Kom morgen terug.\n"
        for line in range(6):
            for i in range(10):
                if [i, line] == [self.x, self.y]:
                    text += "<:home_you:1391301837306466356>"
                elif [i, line] in self.obstacles:
                    index = self.obstacles.index([i, line])
                    if self.obstaclenames[index] == "couch_left":
                        text += "<:couch_left:1391298743382442015>"
                    elif self.obstaclenames[index] == "couch_right":
                        text += "<:couch_right:1391298762797744191>"
                    elif self.obstaclenames[index] == "couch_left_you":
                        text += "<:couch_left_you:1391314692005429348>"
                    elif self.obstaclenames[index] == "couch_right_you":
                        text += "<:couch_right_you:1391314741045235722>"
                else:
                    text += "<:floor:1391299382539976875>"
            text += "\n"
        await interaction.message.edit(content=text, view=self)
        replit.db[str(interaction.user.id)]["x"] = self.x
        replit.db[str(interaction.user.id)]["y"] = self.y
        replit.db[str(interaction.user.id)]["time"] = self.time

    @discord.ui.button(label=chr(8592), style=discord.ButtonStyle.primary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.canmove:
            if interaction.user == self.user:
                if self.x > 0 and [self.x - 1, self.y] not in self.obstacles:
                    self.x -= 1
                else:
                    await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
            else:
                await interaction.response.send_message("Dit huis is niet van jou!", ephemeral=True)
        await self.move(interaction)
    @discord.ui.button(label=chr(8593), style=discord.ButtonStyle.primary)
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.canmove:
            if interaction.user == self.user:
                if self.y > 0 and [self.x, self.y - 1] not in self.obstacles:
                    self.y -= 1
                else:
                    await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
            else:
                await interaction.response.send_message("Dit huis is niet van jou!", ephemeral=True)
        await self.move(interaction)
    @discord.ui.button(label=chr(8595), style=discord.ButtonStyle.primary)
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.canmove:
            if interaction.user == self.user:
                if self.y < 5 and [self.x, self.y + 1] not in self.obstacles:
                    self.y += 1
                else:
                    await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
            else:
                await interaction.response.send_message("Dit huis is niet van jou!", ephemeral=True)
        await self.move(interaction)
    @discord.ui.button(label=chr(8594), style=discord.ButtonStyle.primary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.canmove:
            if interaction.user == self.user:
                if self.x < 10 and [self.x + 1, self.y] not in self.obstacles:
                    self.x += 1
                else:
                    await interaction.response.send_message("Daar kan je niet heen.", ephemeral=True)
            else:
                await interaction.response.send_message("Dit huis is niet van jou!", ephemeral=True)
        await self.move(interaction)
    @discord.ui.button(label="Use", style=discord.ButtonStyle.success, disabled=True, custom_id="use")
    async def use(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.user:
            if [self.x, self.y - 1] in self.obstacles:
                index = self.obstacles.index([self.x, self.y - 1])
                
                if self.obstaclenames[index] == "couch_left":
                    self.obstaclenames[index] = "couch_left_you"
                    self.x = -1
                elif self.obstaclenames[index] == "couch_right":
                    self.obstaclenames[index] = "couch_right_you"
                    self.x = -1
                self.time = time.time()
                for item in self.children:
                    if isinstance(item, discord.ui.Button) and item.custom_id != "use":
                        item.disabled = True
            elif self.x == -1:
                if self.obstaclenames[0] == "couch_left_you":
                    self.obstaclenames[0] = "couch_left"
                    self.x = 4
                elif self.obstaclenames[1] == "couch_right_you":
                    self.obstaclenames[1] = "couch_right"
                    self.x = 5
                self.sat = True
                replit.db[str(interaction.user.id)]["sat"] = True
            if math.floor((time.time() / 120 - self.time / 120)) <= 30:
                self.coins += math.floor((time.time() / 120 - self.time / 120))
            replit.db[str(interaction.user.id)]["obstaclenames"] = self.obstaclenames
            await self.move(interaction)
        else:
            await interaction.response.send_message("Dit huis is niet van jou!", ephemeral=True)
                    
@tree.command(name="home", description="Bekijk je huis.")
async def home(interaction: discord.Interaction):
    print("Home executed!")
    view = HomeView(interaction)
    await interaction.response.send_message("Dit is je huis! Klik op een knop om te laden.", view=view)

@tree.command(name="leaderboard", description="Bekijk de top 10 van de server")
async def leaderboard(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Deze command werkt alleen in servers!")
        return
    members = interaction.guild.members

    memberlist = []
    memberpersons = []
    go = True
    i = 0
    while go:
        if i > 9 or i + 1 == len(members):
            go = False
        try:
            currentmember = replit.db[str(members[i].id)]["coins"]
            if len(memberlist) > 1:
                for x in range(len(memberlist)):
                    if memberlist[x] < currentmember:
                        continue
                    memberlist.insert(x + 1, currentmember)
                    memberpersons.insert(x + 1, members[i].mention)
                    break
            elif len(memberlist) == 1:
                if memberlist[0] > currentmember:
                    memberlist.insert(1, currentmember)
                    memberpersons.insert(1, members[i].mention)
                else:
                    memberlist.insert(0, currentmember)
                    memberpersons.insert(0, members[i].mention)
            else:
                memberlist = [currentmember]
                memberpersons = [members[i].mention]
        except:
            pass
            
        i += 1
    text = "## Leaderboard:\n"
    for x in range(len(memberlist)):
        text += f"{x}. {memberpersons[x]}: 🪙 {str(memberlist[x])} \n"

    await interaction.response.send_message(text)



@tree.command(name="checkminecraftservers", description="Check JippieIsHere's Minecraft Servers.")
async def mcservers(interaction: discord.Interaction):
    print("Checking for Jippie's Minecraft Servers...")
    try:
        await requests.get("https://JippieIsHere-I5SW.aternos.me:46131", timeout=5)
    except Exception as e:
        if "protocol" not in str(e):
            await interaction.response.send_message("**Snapshot online!**")
        else:
            await interaction.response.send_message("Snapshot is not online.")
    try:
        requests.get("https://JippieIsHere.aternos.me:18073")
    except Exception as e:
        channel = interaction.channel
        if "protocol" not in str(e):
            await channel.send("**Normal server online!**")
        else:
            await channel.send("Normal server is not online.")

bot.run(str(os.getenv("BOT_TOKEN")))