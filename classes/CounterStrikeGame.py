import random

class CounterStrikeGame:
    """docstring for CounterStrikeGame."""

    # Private vars start with __

    def __init__(self):
        # Public vars defined here
        self.mapPool = ['Mirage','Inferno','Overpass','Vertigo','Nuke','Train','Dust 2']
        self.currentMaps = []
        self.bannedMaps = []
        self.pickedMaps = []
        self.captains = []
        self.players = []
        self.team1 = []
        self.team2 = []
        self.captainTarget = 0 # Used for insering only 1 captain
        self.turnTracker = 0
        self.teamSize = 5 # 5v5 by default
        self.mapMessageIds = []
        self.messageTracker = []

    def status(self):
        status = ""
        numberOfCaptains = len(self.captains)
        numberOfPlayers = len(self.players)
        status = status + "Team size: " + str(self.teamSize) + "\n"
        status = status + "Number of captains: " + str(numberOfCaptains) + "\n"
        if(numberOfCaptains > 0): # Add captains if there are captains
            if(numberOfCaptains == 1):
                status = status + "Current captains: " + str(self.captains[0].name) + "\n"
            else:
                status = status + "Current captains: " + str(self.captains[0].name) + ", " + str(self.captains[1].name) + "\n"
        status = status + "Number of players: " + str(numberOfPlayers) + "\n"
        if(numberOfPlayers > 0): # If there are players set, add them to the string
            status = status + "Current set players: "
            for player in self.players:
                status = status + player + ","
            status = status + "\n"
        return status

    def check_all(self):
        status = ""
        if(len(self.captains) != 2):
            status = "Not enough captains, you need 2 but only " + str(len(self.captains)) + " were set."
            return status
        elif(len(self.players) != (self.teamSize * 2) - 2):
            status = "Not enough players, you need " + str((self.teamSize * 2) -2) + " but only " + str(len(self.players)) + " were set"
            return status
        else:
            status = "go"
            self.pickedMaps = []
            self.bannedMaps = []
            self.currentMaps = self.mapPool
            return status

    def reset(self):
        self.currentMaps = []
        self.bannedMaps = []
        self.pickedMaps = []
        self.captains = []
        self.players = []
        self.captainTarget = 0 # Used for insering only 1 captain
        self.turnTracker = 0
        self.teamSize = 5 # 5v5 by default
        self.mapMessageIds = []
        self.messageTracker = []
        self.remove_all_messages_from_tracker()

    def set_captains(self, message):
        names = message.mentions
        if(len(names) > 2):
            print("Too many captains, only 2 allowed.")
            return
        if(len(self.captains) == 0 ): # No current captains
            if(len(names) == 1):
                self.captains.append(names)
            else: # 2 captains being added
                self.captains = names
        elif(len(self.captains) < 2 and len(names) == 1): # Just need to add one captain
            if(self.captainTarget == 0):
                self.captains[self.captainTarget] = names
                self.captainTarget = 1
            else:
                self.captains[self.captainTarget] = names
                self.captainTarget = 0
        else: # Replace old captains with new ones
            self.captains = names

    def get_captains(self):
        return self.captains

    def get_current_captain(self):
        if(self.turnTracker % 2 == 0):
            return 0
        else:
            return 1

    def get_turn(self):
        return self.turnTracker

    def set_team_size(self, size):
        self.teamSize = size

    def set_players(self, message):
        if(len(self.players) < (self.teamSize *2) - 2):
            difference = ((self.teamSize*2) -2) - len(self.players)
            if(difference <= ((self.teamSize *2)-2) + len(self.players)):
                names = message.content[11:]
                names = names.split(',')
                for name in names:
                    self.players.append(name)
            else:
                print("difference is too much " + str(difference))
        else:
            print("Too many players need to be added.")

    def get_go_state(self):
        state = ""
        state = state + "Captains: " + str(self.captains[0].name) + ", " + str(self.captains[1].name) + "\n"
        if(self.bannedMaps != []):
            state = state + "Banned maps: "
            for map in self.bannedMaps:
                state = state + map + " "
            state = state + "\n"
        if(self.pickedMaps != []):
            state = state + "Picked maps: "
            for map in self.pickedMaps:
                state = state + map + " "
            state = state + "\n"
        state = state + "Turn tracker: " + str(self.turnTracker) + "(DEBUG)" + "\n"
        # state = state + "Current turn: " + self.captains[self.turnTracker%2].mentions + "\n"
        state = state + "Pick or ban: "
        if(self.pick_or_ban()):
            state = state + "PICK"
        else:
            state = state + "BAN"
        return state

    def pick_or_ban(self):
        if (self.turnTracker >= 2 and self.turnTracker <= 3):
            return True
        else:
            return False

    def add_message_to_tracker(self, message):
        self.messageTracker.append(message)

    def remove_message_from_tracker(self, message):
        removed = False
        for mess in self.messageTracker:
            if(message.id == mess.id):
                self.messageTracker.remove(mess)
                removed = True

        if(removed == False):
            return False
        else:
            return True

    def remove_all_messages_from_tracker(self):
        for mess in self.messageTracker:
            self.messageTracker.remove(mess)

    def get_message_tracker(self):
        return self.messageTracker

    def get_current_maps(self):
        return self.currentMaps

    def ban_map(self, mapString):
        for map in self.currentMaps:
            if(map == mapString):
                self.currentMaps.remove(mapString)
                self.bannedMaps.append(mapString)
                self.turnTracker = self.turnTracker + 1
            else:
                print("No map with this name?")

    def pick_map(self, mapString):
        for map in self.currentMaps:
            if(map == mapString):
                self.currentMaps.remove(mapString)
                self.pickedMaps.append(mapString)
                self.turnTracker = self.turnTracker + 1
            else:
                print("No map with this name?")

    def randomise_teams(self):
        specificNumbers = [0,1,2,3,4,5,6,7]
        counter = 0
        self.team1 = []
        self.team2 = []
        self.team1.append(self.captains[0].name)
        self.team2.append(self.captains[1].name)
        for player in self.players:
            number = random.choice(specificNumbers)
            specificNumbers.remove(number)
            if(counter < 4):
                self.team1.append(self.players[number])
            else:
                self.team2.append(self.players[number])
            counter += 1


    def get_end_message(self):
        string = ""
        string += "Final result:\n"
        string = string + "Picked maps: " + self.pickedMaps[0] + ", " + self.pickedMaps[1] + "\n"
        string = string + "Last map: " + self.pickedMaps[2] + "\n"
        string += "Teams: \n\n"
        string += "Team 1: \n"
        counter = 1
        for player in self.team1:
            string = string + str(counter) + ". " + player + "\n"
            counter += 1
        string += "\n"
        string += "Team 2: \n"
        counter = 1
        for player in self.team2:
            string = string + str(counter) + ". " + player + "\n"
            counter += 1
        return string
