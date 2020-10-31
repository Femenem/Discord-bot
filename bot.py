import discord
import json
import random
from classes.CounterStrikeGame import CounterStrikeGame
from classes.Movie import Movie
from classes.Elevator import Elevator
import sqlite3
import logging

# create logger with 'spam_application'
logger = logging.getLogger('god_bot')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('bot.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


helpMessage = """
```
##### GOD COMMANDS #####
!god help = This help message.
!god dev = The open source github repo.
### Randomised commands ###
!god choice [choice, choice, choice] = Picks an option at random.
!god coin = Flip a coin.

### Movie commands ###
!god movie [title] = Get info about a specific movie.

### CS commands ###
!cs status = See the current status of the CS game.
!cs reset = Resets the CS game to default settings. (Use this after completing a game)
!cs mode [comp|br] = Sets the mode for the cs game (Competitive or Battle Royale)
!cs captains [@name, @name] = Sets the captains for the cs game
!cs players [name,name,name,name...] = Sets the players for the cs game
!cs go = Starts the veto/random teams process.
!cs randomise = Re-randomise the teams for the cs game. (used after !cs go)
```
"""

class Bot(discord.Client):
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    go = False # Used for cs
    movieLists = []

    async def on_ready(self):
        self.csGame = CounterStrikeGame();
        self.go = False
        self.targetGuild = None
        self.elevator = None
        self.load_movie_lists()
        logger.info('Logged on as ' + self.user.name)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            if self.go == True: # Running cs sunday
                self.csGame.add_message_to_tracker(message)
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        if message.content.startswith('!god'):
            option = message.content[5:].split(' ')
            if(option[0].lower() == 'help'):
                await message.channel.send(helpMessage)
            if(option[0].lower() == 'dev'):
                devUrl = "https://github.com/Mattmor/Discord-bot"
                await message.channel.send("This is the dev repo: " + devUrl)
            #####################
            # Movie options     #
            #####################
            if(option[0].lower() == 'movie'):
                movieString = ""
                for op in option:
                    if(op != 'movie'):
                        movieString += op + " "
                movie = Movie(movieString)
                await message.channel.send(movie.print_movie())
            #####################
            # Random options    #
            #####################
            if(option[0] == 'choice'):
                await self.random_choice(message)
            if(option[0] == 'flip'):
                await self.coin_flip(message)


        #####################
        # Cs options        #
        #####################
        if message.content.startswith('!cs'):
            option = message.content[4:].split(' ')

            if(option[0] == 'mode'):
                if(len(option) <= 1): # No mode specified
                    await message.channel.send("Please specify the mode, Comp or Br")
                else:
                    if(option[1].lower() == "comp" or option[1].lower() == "br"):
                        self.csGame.set_mode(option[1].lower())
                        await message.channel.send("Mode set to: " + self.csGame.get_mode(), delete_after=10)
                    else:
                        await message.channel.send("Mode can only be set to comp or br, dumbass")

            if(option[0] == 'randomise'):
                if(len(option) == 1):
                    if(self.go == True):
                        self.csGame.randomise_teams()
                        for message in self.csGame.get_message_tracker():
                            if(message.content.startswith("Final result:")):
                                await message.edit(content=self.csGame.get_end_message())
                    else:
                        await message.channel.send("You cant randomise teams before using !cs go")
                elif(option[1] == 'teams'):
                    await self.cs_random_teams(message)

            if(option[0] == 'status'):
                if(self.go == False):
                    await message.channel.send(self.csGame.status())
                else:
                    await message.channel.send(self.csGame.get_end_message())
            if(option[0] == 'start' or option[0] == 'reset'):
                self.csGame.remove_all_messages_from_tracker()
                self.csGame.reset()
                self.go = False
                await message.channel.send("Reset cs game")
            if(option[0] == 'captain' or option[0] == 'captains'):
                if(message.mentions == []):
                    await message.channel.send("You gotta @ people for caprains")
                else:
                    if(self.go == True):
                        await message.channel.send("You cant set captains after using !cs go. Please !cs reset before adding new captains")
                    else:
                        self.csGame.set_captains(message)
                        await message.channel.send("Added captains", delete_after=5)
            if(option[0] == 'player' or option[0] == 'players'):
                if(self.go == True):
                    await message.channel.send("You cant set players after using !cs go. Please !cs reset before adding new players")
                else:
                    self.csGame.set_players(message)
                    await message.channel.send("Added players", delete_after=5)
            if(option[0] == 'go'):
                canGo = self.csGame.check_all()
                if(canGo == "go" and self.go == False): ## All set so we can go for comp
                    self.go = True
                    await message.channel.send(self.csGame.get_go_state())
                    captains = self.csGame.get_captains()
                    await message.channel.send("Current turn: " + str(captains[0].mention)) # TODO: Change to be crrent captain
                    maps = self.csGame.get_current_maps()
                    for map in maps:
                        await message.channel.send(str(map))
                    trackedMessages = self.csGame.get_message_tracker()
                    for trackedMessage in trackedMessages:
                        for map in maps:
                            if(trackedMessage.content == map):
                                await trackedMessage.add_reaction("🚫") # 🚫 ✅

                elif(canGo == "gobr" and self.go == False): # All set so we can go for br
                    self.csGame.do_br_teams()
                    await message.channel.send(self.csGame.print_br_teams())
                else: # Check failed so print message
                    if(self.go == True):
                        await message.channel.send("You have to !cs reset before starting another game")
                    else:
                        await message.channel.send(canGo)

        if(message.content.lower().startswith('!floor')):
            if(message.guild == self.targetGuild):
                if(message.author.voice != None):
                    floor = message.content[7:]
                    # print("trying to add user...")
                    await self.elevator.add_user(message, floor)
                else: # User not in a voice channel
                    await message.channel.send("You need to be connected to a voice channel first.")
            else: # Not target guild
                logger.info("Error, not target guild")


    async def on_reaction_add(self, reaction, user):
        if(self.go == True): # Running cs sunday
            if(reaction.message.author == self.user): # If this bot put the message there
                captains = self.csGame.get_captains()
                turn = self.csGame.get_turn()
                captainTurn = turn % 2 # Relating to 0 for first captain, 1 for second
                if(captains[captainTurn] == user): ## Is current captain picking
                    map = reaction.message.content
                    if(turn >= 2 and turn <= 3):
                        self.csGame.pick_map(map)
                        turn = self.csGame.get_turn()
                        await self.update_maps_message(turn)
                    else:
                        self.csGame.ban_map(map)
                        turn = self.csGame.get_turn()
                        await self.update_maps_message(turn)
                        if(turn == 6): # End conditon when all maps have been picked/banned
                            for message in self.csGame.get_message_tracker():
                                if(len(message.content) > 10):
                                    ## Content too long to be map name.
                                    continue
                                else:
                                    self.csGame.pick_map(message.content)
                                    break

                            await self.end_go(reaction)

    async def delete_all_tracked_messages(self):
        for message in self.csGame.get_message_tracker(): # Delete all tracked messages
            await message.delete()

    async def end_go(self, reaction):
        self.csGame.randomise_teams()
        await self.delete_all_tracked_messages()
        self.csGame.remove_all_messages_from_tracker()
        await reaction.message.channel.send(self.csGame.get_end_message())

    async def update_maps_message(self, turn):
        maps = self.csGame.get_current_maps()
        for message in self.csGame.get_message_tracker():
            if(len(message.content) > 10):
                ## Content too long to be map name.
                continue
            delete = True
            for map in maps: # Linear search
                if(message.content == map): # If map still in current maps
                    delete = False # Dont delete
            if(delete == True):
                await message.delete()
                self.csGame.remove_message_from_tracker(message)
                continue

        for message in self.csGame.get_message_tracker(): # Update reactions
            if(len(message.content) > 10):
                ## Content too long to be map name.
                continue

            if(message.reactions != []): # message has reactions
                if(turn == 2):
                    await message.clear_reactions()
                    await message.add_reaction("✅")
                elif(turn == 4):
                    await message.clear_reactions()
                    await message.add_reaction("🚫")

        ### Update current turn
        for message in self.csGame.get_message_tracker():
            if(message.content.startswith("Captains: ")):
                await message.edit(content=self.csGame.get_go_state())
            if(message.content.startswith("Current turn:")):
                captains = self.csGame.get_captains()
                turn = self.csGame.get_current_captain()
                # Pls clean this up
                newMessage = "Current turn: <@" + str(captains[turn].id) + ">"
                await message.edit(content=newMessage)
                break

    async def random_choice(self, message):
        choices = message.content[11:].split(',')
        randomNumber = random.randint(0, len(choices)-1)
        await message.channel.send(choices[randomNumber])

    async def coin_flip(self, message):
        roll = random.randint(0, 1)
        if (roll == 0):
            coin = "heads"
        elif (roll == 1):
            coin = "tails"
        await message.channel.send("<@" + str(message.author.id) + "> flipped a coin and it landed on " + coin)

    # def load_movie_lists(self):
    #     # TODO: Load MovieLists on startup
    #     with sqlite3.connect('data/movies.db') as db:
    #         c = db.cursor()
    #         c.execute()

loginFile= "settings/login.json"
loginData = open(loginFile)
login = json.load(loginData)
status = discord.Activity(name="!god help", state="!god help", type=discord.ActivityType.playing, details="!god help")
client = Bot(activity=status)

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if discord.opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            discord.opus.load_opus(opus_lib)
            return
        except OSError:
            pass

        raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

opusLoaded = load_opus_lib()
if(opusLoaded):
    print("Opus already loaded")
    client.run(login['token'])
else:
    discord.opus.load_opus('libopus-0.dll')
    client.run(login['token'])
