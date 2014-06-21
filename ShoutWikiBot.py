"""
    TODO add version, copyright, e.t.c., e.t.c.

    Usage:
    1) Add the following to LocalSettings.php

        $wgRCFeeds['exampleirc'] = array(
            'formatter' => 'IRCColourfulRCFeedFormatter',
            'uri' => 'udp://localhost:1338',
            'add_interwiki_prefix' => false, 
            'omit_bots' => true,
        );
"""

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

""" User-defined variables """
HOST = "irc.freenode.net"
IRC_PORT = 6667
CHANNEL = "#cook879"
NICKNAME = "cook879Bot"
UDP_PORT = 1338
""" End user-defined variables """

recver = None

class ShoutWikiBot( irc.IRCClient ):
    """ Bot class inherits from irc.IRCClient
            see https://twistedmatrix.com/documents/14.0.0/api/twisted.words.protocols.irc.IRCClient.html
    """

    nickname = NICKNAME
        
    def connectionMade( self ):
        irc.IRCClient.connectionMade( self )

    def connectionLost( self, reason ):
        irc.IRCClient.connectionLost( self, reason )

    def signedOn( self ):
        global recver
        self.join( CHANNEL )
        recver = self

    def gotUDP( self, broadcast ):
        self.msg( CHANNEL, broadcast )

class ShoutWikiBotFactory( protocol.ClientFactory ):
    """ Factory class inherits from ClientFactory
            see https://twistedmatrix.com/documents/14.0.0/api/twisted.internet.protocol.ClientFactory.html
    """

    def buildProtocol( self, addr ):
        b = ShoutWikiBot()
        b.factory = self
        return b

    def clientConnectionLost( self, connector, reason ):
        """ If we get disconnected, try and reconnect to server. """
        connector.connect()

    def clientConnectionFailed( self, connector, reason ):
        print "Connection failed: ", reason
        #TODO stop or reconnect?
        #reactor.stop()
        #connector.connect()

class Echo( protocol.DatagramProtocol ):

    def datagramReceived( self, data, (host, port) ):
        global recver
        recver.gotUDP( data )
    
# Create factory protocol and application
f = ShoutWikiBotFactory()

# UDP stuff
reactor.listenUDP( UDP_PORT, Echo() )

# Connect factory to host and port
reactor.connectTCP( HOST, IRC_PORT, f )

# Run bot
reactor.run()
