import random

class CounterStrikeGame:
    """docstring for CounterStrikeGame."""

    # Protected vars start with __

    def __init__(self):
        # Private vars defined here with self.<varName>
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
        self.mode = "comp"
        self.playerTeams = {} # Used for BR mode only.

    def status(self):
        status = ""
        numberOfCaptains = len(self.captains)
        numberOfPlayers = len(self.players)
        if(self.mode == "comp"):
            status += "Mode: " + self.mode + "\n"
            status += "Team size: " + str(self.teamSize) + "\n"
            status += "Number of captains: " + str(numberOfCaptains) + "\n"
            if(numberOfCaptains > 0): # Add captains if there are captains
                if(numberOfCaptains == 1):
                    status += "Current captains: " + str(self.captains[0].name) + "\n"
                else:
                    status += "Current captains: " + str(self.captains[0].name) + ", " + str(self.captains[1].name) + "\n"
            status += "Number of players: " + str(numberOfPlayers) + "\n"
            if(numberOfPlayers > 0): # If there are players set, add them to the string
                status += "Current set players: "
                for player in self.players:
                    status += player + ","
                status += "\n"
            return status
        elif(self.mode == "br"):
            status += "Mode: " + self.mode + "\n"
            status += "Number of players: " + str(numberOfPlayers) + "\n"
            if(numberOfPlayers > 0): # If there are players set, add them to the string
                status += "Current set players: "
                for player in self.players:
                    status += player + ","
                status += "\n"
            return status

    def check_all(self):
        status = ""
        if(self.mode == "comp"):
            if(len(self.captains) != 2):
                status += "Not enough captains, you need 2 but only " + str(len(self.captains)) + " were set."
                return status
            elif(len(self.players) != (self.teamSize * 2) - 2):
                status += "Not enough players, you need " + str((self.teamSize * 2) -2) + " but only " + str(len(self.players)) + " were set"
                return status
            else:
                status += "go"
                self.pickedMaps = []
                self.bannedMaps = []
                self.currentMaps = self.mapPool
                return status
        else: # Danger zone
            if(len(self.players)%2 != 0): # Not Even number of players
                status += "Not an even number of players. You courrently have " + str(len(self.players)) + " players set."
                return status
            else: # Even number of players
                status += "gobr"
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
        self.mode = "comp"
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
        names = message.content[11:]
        names = names.split(',')
        if(self.mode == "comp"):
            if(len(names) == (self.teamSize*2) -2): # Replace the teams
                self.players = names
            elif(len(self.players) < (self.teamSize *2) - 2):
                difference = ((self.teamSize*2) -2) - len(self.players)
                if(difference <= ((self.teamSize *2)-2) + len(self.players)):
                    for name in names:
                        self.players.append(name)
                else:
                    print("difference is too much " + str(difference))
            else:
                print("Too many players need to be added.")
        elif(self.mode == "br"):
            if(len(names) % 2 == 0): # Even number of players
                self.players = names
            else:
                print("Not an even amount of players.")

    def get_go_state(self):
        state = ""
        state += "Captains: " + str(self.captains[0].name) + ", " + str(self.captains[1].name) + "\n"
        if(self.bannedMaps != []):
            state += "Banned maps: "
            for map in self.bannedMaps:
                state += map + " "
            state += "\n"
        if(self.pickedMaps != []):
            state += "Picked maps: "
            for map in self.pickedMaps:
                state += map + " "
            state += "\n"
        # state += "Turn tracker: " + str(self.turnTracker) + "(DEBUG)" + "\n"
        # state += "Current turn: " + self.captains[self.turnTracker%2].mentions + "\n"
        state += "Pick or ban: "
        if(self.pick_or_ban()):
            state += "PICK"
        else:
            state += "BAN"
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
        specificNumbers = []
        for x in range(0, (len(self.teamSize)*2)-2): # Make list with the correct amount of numbers needed
            specificNumbers.append(x)
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
        string += "Picked maps: " + self.pickedMaps[0] + ", " + self.pickedMaps[1] + "\n"
        string += "Last map: " + self.pickedMaps[2] + "\n"
        string += "Teams: \n\n"
        string += "Team 1: \n"
        counter = 1
        for player in self.team1:
            string += str(counter) + ". " + player + "\n"
            counter += 1
        string += "\n"
        string += "Team 2: \n"
        counter = 1
        for player in self.team2:
            string += str(counter) + ". " + player + "\n"
            counter += 1
        return string

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def do_br_teams(self):
        specificNumbers = []
        for x in range(0, len(self.players)): # Make list with the correct amount of numbers needed
            specificNumbers.append(x)
        for player in self.players:
            number = random.choice(specificNumbers)
            specificNumbers.remove(number)
            self.playerTeams[number] = player

    def print_br_teams(self):
        status = ""
        for number, player in self.playerTeams.items():
            if number < 2:
                status +=  "Team 1: " + player + "\n"
            elif number < 4:
                status +=  "Team 2: " + player + "\n"
            elif number < 6:
                status +=  "Team 3: " + player + "\n"
            elif number < 8:
                status +=  "Team 4: " + player + "\n"
            elif number < 10:
                status +=  "Team 5: " + player + "\n"
            elif number < 12:
                status +=  "Team 6: " + player + "\n"
            elif number < 14:
                status +=  "Team 7: " + player + "\n"
        return status
