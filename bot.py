import discord
from discord import app_commands
from discord.ext import commands
import os
import dotenv
import asyncio
from typing import Optional

dotenv.load_dotenv()

autoreplier = False

intents = discord.Intents.default()
intents.message_content = True  # Nodig om berichten te lezen
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f'Bot is online als {bot.user}')
    await tree.sync()

@bot.command()
async def ping(ctx):
    print("Playing a game of Ping Pong...")
    await ctx.send("Pong!")
@bot.event
async def on_message(msg):
    global autoreplier, autoreply_text
    if not msg.author.bot and autoreplier and msg.channel == autoreply_channel:
        print("Autoreply off.")
        await autoreply_channel.send(autoreply_text)
        autoreplier = False
    await bot.process_commands(msg)

@tree.command(name="autoreply", description="Antwoordt meteen als iemand iets zegt")
@app_commands.describe(text="Wat moet de bot zeggen?")
async def autoreply(interaction: discord.Interaction, text: str):
    print("Autoreply on.")
    global autoreplier
    global autoreply_text
    global autoreply_channel
    autoreplier = True
    autoreply_text = text
    autoreply_channel = interaction.channel
    await interaction.response.send_message(f'Autoreply is geactiveerd met tekst: "{text}"!', ephemeral=True)


@tree.command(name="say", description="Zegt iets")
@app_commands.describe(text="Wat moet de bot zeggen?",
                       time="Hoe lang moet het duren voordat de bot dit zegt? (in seconden)",
                       message_id="Waarop moet de bot reageren? Geef een Message ID.")
async def say(interaction: discord.Interaction, text: str, time: Optional[int] = None, message_id: Optional[str] = None):
    print("/say executed.")
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
        await channel.send(text)

Vars = {}
var_group = app_commands.Group(name="var", description="Commands met variabelen.")
async def name_vars(interaction):
    text = "## Variabelen:\n"
    print(list(Vars.keys()))
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


class MyView(discord.ui.View):
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
    print("Platformer executed")
    view = MyView(interaction)
    await interaction.channel.send("🟦🟦🟦🟦🟦🟦\n🟦🟦🟦🟦⬛🟦\n🟨🟦🟦⬛🟦🟦", view=view)

bot.run(str(os.getenv("BOT_TOKEN")))