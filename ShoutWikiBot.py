# -*- coding: cp1252 -*-
"""
    RecentChanges bot for ShoutWiki

    Usage:
    Add the following to LocalSettings.php

        $wgRCFeeds['exampleirc'] = array(
            'formatter' => 'IRCColourfulRCFeedFormatter',
            'uri' => 'udp://localhost:1338',
            'add_interwiki_prefix' => true, 
            'omit_bots' => true,
        );


    @version 0.2
    @author Richard Cook <cook879@shoutwiki.com>
    @copyright Copyright � 2015 ShoutWiki
    @license http://www.gnu.org/copyleft/gpl.html GNU General Public License 3.0 or later
"""


# User-defined variables
HOST = "irc.freenode.net"
IRC_PORT = 6667
CHANNEL = "#ShoutWiki-cvn" 
#CHANNEL = "#cook879" # test channel
NICKNAME = "ShoutWikiRC"
UDP_PORT = 1338
IRC_OPERATOR = '@unaffiliated/cook879'
IRC_OPERATOR2 = '@wikimedia/Lcawte'
IRC_OPERATOR3 = '@MediaWiki/Jack-Phoenix'

# End user-defined variables


import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

recver = None

class ShoutWikiBot( irc.IRCClient ):
    """ Bot class inherits from irc.IRCClient
            see https://twistedmatrix.com/documents/14.0.0/api/twisted.words.protocols.irc.IRCClient.html
    """

    # self.nickname is needed for something - I forget what
    nickname = NICKNAME
        
    def signedOn( self ):
        global recver
        self.join( CHANNEL )
        recver = self

    def kickedFrom( self, channel, kicker, message ):
        self.join( channel )

    def gotUDP( self, broadcast ):
        self.msg( CHANNEL, broadcast )

    def privmsg( self, user, channel, message ):
        if channel.lower() == self.nickname.lower():
            if re.search( IRC_OPERATOR, user ) or re.search( IRC_OPERATOR2, user ) or re.search( IRC_OPERATOR3, user ):
                if message.lower() == 'quit':
                    reactor.stop()


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
        connector.connect()

class Echo( protocol.DatagramProtocol ):
    """ Handles the recieving of recent changes data
        Inherits from DatagramProtocol
            see https://twistedmatrix.com/documents/14.0.0/api/twisted.internet.protocol.DatagramProtocol.html
    """
        
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
