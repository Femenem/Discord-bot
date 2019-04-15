import discord
import json
import random

class Bot(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        if message.content.startswith('!cs teams'):
            await self.cs_random_teams(message)

    async def cs_random_teams(self, message):
        specificNumbers = [0,1,2,3,4,5,6,7]
        names = message.content[9:].split(',')
        randomList = {}
        if len(names) != 8:
            await message.channel.send("There aren't enough people for cs, you need 8 (excluding captains) but you gave me " + str(len(names)))
            return
        for x in range(0, 8):
            number = random.choice(specificNumbers) # pick random number
            specificNumbers.remove(number) # remove number from list
            randomList[number] = names[x] # set name and random number

        print(randomList)

        adreans_team_string = "Team 1: \n 1: Adrean\n"
        fins_team_string = "Team 2: \n 1: Fin\n"
        for x in range(0, 4):
            adreans_team_string = adreans_team_string + str(x+2) + ": " + str(randomList.get(x)) + "\n"
            fins_team_string = fins_team_string + str(x+2) + ": " + str(randomList.get(x+4)) + "\n"

        await message.channel.send(adreans_team_string + "\n" + fins_team_string)

loginFile= "settings/login.json"
loginData = open(loginFile)
login = json.load(loginData)
client = Bot()
client.run(login['token'])
