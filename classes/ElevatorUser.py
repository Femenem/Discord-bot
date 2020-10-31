class ElevatorUser():
    """docstring for User."""

    def __init__(self, currentFloor, destinationFloor, user):
        self.originFloor = currentFloor
        self.destinationFloor = destinationFloor
        if(currentFloor.position < destinationFloor.position): # Top floor is 0
            self.goingUp = False
        else:
            self.goingUp = True
        self.userInfo = user

    def get_origin_floor(self):
        return self.originFloor

    def get_destination_floor(self):
        return self.destinationFloor

    def going_up(self):
        return self.goingUp

    def get_user_info(self):
        return self.userInfo
