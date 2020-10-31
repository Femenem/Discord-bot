from classes.ElevatorUser import ElevatorUser
import discord
import atexit
import asyncio
from time import sleep
import logging

class Elevator():
    """docstring for Elevator."""

    def __init__(self, channels, bot):
        self.bot = bot
        self.requests = [] # Pickup and drop off request
        self.channels = []
        self.riding = [] # Currently in elevator
        self.currentFloor = None
        self.currentDestination = None
        self.connected = False
        self.goingUp = False
        self.VoiceClient = None
        self.running = False
        # self.volume = 0.2
        self.lastMessage = None
        # self.elevatorDing = discord.FFmpegPCMAudio("music/elevatorDing.mp3")
        # self.volume = discord.PCMVolumeTransformer(self.elevatorDing)
        self.set_channels(channels)
        # atexit.register(self.disconnect)
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    async def run(self):
        # Setup
        if(len(self.requests) > 0):
            await self.connect()
            self.running = True
            elevatorMusic = discord.FFmpegPCMAudio("music/simsElevator.mp3")
            elevatorDing = discord.FFmpegPCMAudio("music/elevatorDing.mp3")

        # Loop
        while self.running:
            pickupDropoffFlag = False
            if(len(self.requests) > 0):
                if(len(self.riding) < 1): # No-one riding
                    self.currentDestination = self.requests[0].get_origin_floor()
                else:
                    self.currentDestination = self.requests[0].get_destination_floor()

                for user in self.requests: # Add requests to riding if possible
                    if(user.get_origin_floor() == self.currentFloor and user.going_up() == self.requests[0].going_up()):
                        if(user in self.riding):
                            self.logger.info("User already riding")
                        else:
                            # User on same floor as elevator and going in same direction
                            self.riding.append(user) # Pick user up
                            self.logger.info("Added user to riding")
                            pickupDropoffFlag = True

                minusByNumber = 0 # Hacky pls fix
                for userNumber in range(len(self.riding)): # Remove riding requests if possible
                    user = self.riding[userNumber-minusByNumber]
                    self.logger.info(user.get_user_info().name)
                    if(user.get_destination_floor() == self.currentFloor): # User needs to get out
                        pickupDropoffFlag = True
                        minusByNumber += 1
                        self.riding.remove(user)
                        self.requests.remove(user)
                        self.logger.info("Removed user from elevator")

            if(pickupDropoffFlag):
                # print("Stopping")
                # self.VoiceClient.stop()
                # self.VoiceClient.play(discord.PCMVolumeTransformer(elevatorDing, volume=0.5))
                # if(not self.bot.voice_clients[0].is_playing()): # Music not playing
                #     self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(self.elevatorDing, volume=0.2))
                # else:
                #     self.bot.voice_clients[0].source = discord.PCMVolumeTransformer(self.elevatorDing, volume=0.2)
                # if(self.bot.voice_clients[0].is_playing()):
                #     self.bot.voice_clients[0].stop()
                await asyncio.sleep(3)
                # self.VoiceClient.stop()
                pickupDropoffFlag = False
                # self.bot.voice_clients[0].stop()

            # End condition after dropping off user
            if(len(self.requests) == 0): # Last request
                self.logger.info("Last request!")
                self.VoiceClient.stop()
                await self.disconnect()
                self.VoiceClient = None
                self.running = False # Set to false on last request
                return

            try:
                if(not self.VoiceClient.is_playing()): # Music not playing
                    self.VoiceClient.play(discord.PCMVolumeTransformer(elevatorMusic, volume=0.5))
            except Exception as e:
                print("Cannot play music")

            await asyncio.sleep(4)

            if(len(self.riding) > 0): # someone currently riding
                self.goingUp = self.riding[0].going_up()
            else:
                self.compare_floors_and_update_direction(self.requests[0].get_origin_floor())
            # Move floors
            floorIndex = self.channels.index(self.currentFloor)
            if(self.goingUp):
                # print("Going up")
                aboveFloor = self.channels[floorIndex-1]
                await self.VoiceClient.move_to(aboveFloor)
                self.logger.info(aboveFloor.name)
                self.currentFloor = aboveFloor
                self.logger.info(self.currentFloor.name)
                for user in self.riding:
                    if(user.get_user_info().voice != None):
                        await user.get_user_info().move_to(aboveFloor)
                    else:
                        self.riding.remove(user)
                        self.requests.remove(user)
                        await self.lastMessage.channel.send("Fuck you "  + user.get_user_info().mention + "!")
            else:
                # print("Going down")
                belowFloor = self.channels[floorIndex+1]
                await self.VoiceClient.move_to(belowFloor)
                self.logger.info(belowFloor.name)
                self.currentFloor = belowFloor
                self.logger.info(self.currentFloor.name)
                for user in self.riding:
                    if(user.get_user_info().voice != None):
                        await user.get_user_info().move_to(belowFloor)
                    else:
                        self.riding.remove(user)
                        self.requests.remove(user)
                        await self.lastMessage.channel.send("Fuck you " + user.get_user_info().mention + "!")

            #self.VoiceClient = discord.utils.get(self.lastMessage.guild.voice_channels, guild__name='Dozy Bot Testing Grounds')
            self.VoiceClient = self.lastMessage.guild.voice_client

    def compare_floors_and_update_direction(self, floor):
        if(self.currentFloor.position > floor.position): # Need to go up
            self.goingUp = True
        else: # Need to go down
            self.goingUp = False

    def between_current_and_destination(self, floor):
        if(self.goingUp): # Values will be decending
            return self.currentFloor.position > floor.position
        else:
            return self.currentFloor.position < floor.position

    def update_current_floor(self, floor):
        if(self.VoiceClient != None):
            self.currentFloor = floor
        else:
            self.logger.info("cannot get current channel when not connected")

    def set_channels(self, channels):
        self.channels = channels

    def get_channels(self):
        return self.channels

    async def add_user(self, message, floor):
        addUser = True
        # Check for user already in requests. Only 1 request per user
        for user in self.requests:
            if(user.get_user_info() == message.author):
                addUser = False
                await message.channel.send("You can only request the elevator once " + message.author.mention)

        if(addUser):
            currentFloor = message.author.voice.channel
            destinationFloor = None
            self.lastMessage = message
            ## Match requested floor with channels list
            for channel in self.channels:
                if(floor.lower() in channel.name.lower()):
                    destinationFloor = channel
            self.logger.info(floor.lower())
            if(destinationFloor != None):
                userRequest = ElevatorUser(currentFloor, destinationFloor, message.author)
                self.requests.append(userRequest)
                self.logger.info("request created!")
                if(self.running == False):
                    await self.run()
            else:
                await message.channel.send("Cannot find that floor.")

    async def connect(self):
        try:
            if(self.VoiceClient == None):
                groundFloor = discord.utils.get(self.channels, name='Ground Floor')
                self.VoiceClient = await groundFloor.connect()
                self.update_current_floor(groundFloor)
                self.logger.info("connected")
            else:
                if(self.VoiceClient.is_connected()):
                    self.logger.info("Is already connected")
                else:
                    groundFloor = discord.utils.get(self.channels, name='Ground Floor')
                    self.VoiceClient = await groundFloor.connect()
                    self.update_current_floor(groundFloor)
        except Exception as e:
            self.logger.info("Error: " + str(e))
            await self.disconnect()
            return


    async def disconnect(self):
        if(self.VoiceClient != None):
            await self.VoiceClient.disconnect()
            self.VoiceClient = None
            self.logger.info("Disconnected!")

    def update_voice_channels(self, voice_channels):
        self.channels = voice_channels
