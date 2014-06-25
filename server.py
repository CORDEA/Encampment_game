from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from time import sleep

class GameChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Network_getRoute(self, data):
        print("get route")
        route = data["route"]
        bomb  = data["bomb"]
        player = data["player"]
        self._server.sendRoute(route, bomb, player)

    def Network_getStartFlag(self, data):
        global players
        start = data["start"]
        player = data["player"] + 1
        players.append(player)
        print("Ready: " +  str(player))
        if len(players) == 2:
            self._server.whistle()

    def Network_getEndFlag(self, data):
        global endPlayer
        player = data["endPlayer"]
        endPlayer.append(player)
        if len(endPlayer) == 2:
            players = []
 
class GameServer(Server):
    channelClass = GameChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.queue = None
        self.games = []
        print("Server launched")
 
    def Connected(self, channel, addr):
        print 'New connection:', channel

        if self.queue == None:
            self.queue = Game(channel)
            print("queue = None")
        else:
            self.queue.player1=channel
            self.queue.player0.Send({"action": "startgame","player":0})
            self.queue.player1.Send({"action": "startgame","player":1})
            self.games.append(self.queue)
            self.queue=None
    
    def sendRoute(self, route, bomb, player):
        for i in self.games:
            game = i
        print("send route")
        if player == 1:
            game.player0.Send({"action": "getRoute", "route": route, "bomb": bomb})
        else:
            game.player1.Send({"action": "getRoute", "route": route, "bomb": bomb})

    def whistle(self):
        for i in self.games:
            game = i
        print("whistle")
        game.player0.Send({"action": "whistle", "start": True})
        game.player1.Send({"action": "whistle", "start": True})

    def launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

class Game:
    def __init__(self, player0):
        self.player0 = player0
        self.player1 = None


if __name__=='__main__':
    players = []
    endPlayer = []
    

    address = raw_input("Host:Port : ")
    if not address:
        host, port= "localhost", 8000
    else:
        host,port = address.split(":")
        gameServer = GameServer(localaddr=(host,int(port)))
        gameServer.launch()
