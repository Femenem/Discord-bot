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
        if len(names) != 10:
            await message.channel.send("There aren't enough people for cs, you need 10 names (First 2 captains) but you gave me " + str(len(names)-1))
            return
        captains = [names[0], names[1]]
        del names[0:2]
        for x in range(0, 8):
            number = random.choice(specificNumbers) # pick random number
            specificNumbers.remove(number) # remove number from list
            randomList[number] = names[x] # set name and random number

        # print(names) DEBUG MESSAGE 

        team_1_string = "Team 1: \n 1: " + str(captains[0]) + "\n"
        team_2_string = "Team 2: \n 1: " + str(captains[1]) + "\n"
        for x in range(0, 4):
            team_1_string = team_1_string + str(x+2) + ": " + str(randomList.get(x)) + "\n"
            team_2_string = team_2_string + str(x+2) + ": " + str(randomList.get(x+4)) + "\n"

        await message.channel.send(team_1_string + "\n" + team_2_string)

loginFile= "settings/login.json"
loginData = open(loginFile)
login = json.load(loginData)
client = Bot()
client.run(login['token'])
