import discord
import json
import random
from classes.CounterStrikeGame import CounterStrikeGame
from classes.Movie import Movie

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
    go = False # Used for cs

    async def on_ready(self):
        self.csGame = CounterStrikeGame();
        self.go = False
        print('Logged on as', self.user)

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


    # async def cs_random_teams(self, message):
    #     specificNumbers = [0,1,2,3,4,5,6,7]
    #     names = message.content[14:].split(',')
    #     randomList = {}
    #     if len(names) != 10:
    #         await message.channel.send("There aren't enough people for cs, you need 10 names (First 2 captains) but you gave me " + str(len(names)-1))
    #         return
    #     captains = [names[0], names[1]]
    #     del names[0:2]
    #     for x in range(0, 8):
    #         number = random.choice(specificNumbers) # pick random number
    #         specificNumbers.remove(number) # remove number from list
    #         randomList[number] = names[x] # set name and random number
    #
    #
    #     team_1_string = "Team 1: \n 1: " + str(captains[0]) + "\n"
    #     team_2_string = "Team 2: \n 1: " + str(captains[1]) + "\n"
    #     for x in range(0, 4):
    #         team_1_string = team_1_string + str(x+2) + ": " + str(randomList.get(x)) + "\n"
    #         team_2_string = team_2_string + str(x+2) + ": " + str(randomList.get(x+4)) + "\n"
    #
    #     await message.channel.send(team_1_string + "\n" + team_2_string)

loginFile= "settings/login.json"
loginData = open(loginFile)
login = json.load(loginData)
# type = discord.ActivityType(value=discord.ActivityType.playing)
status = discord.Activity(name="!god help", state="!god help", type=discord.ActivityType.playing, details="!god help")
client = Bot(activity=status)
client.run(login['token'])
