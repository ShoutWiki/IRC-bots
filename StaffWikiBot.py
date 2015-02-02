# -*- coding: cp1252 -*-
"""
    Bot for staff wiki

    Requirements:
        * Python 2.7
        * Twisted 14.0.0 (https://twistedmatrix.com)
        * bugzillatools 0.5.3.1 (https://pypi.python.org/pypi/bugzillatools)
    

    Usage:
    Add the following to LocalSettings.php

        $wgRCFeeds['exampleirc'] = array(
            'formatter' => 'IRCColourfulRCFeedFormatter',
            'uri' => 'udp://localhost:1338',
            'add_interwiki_prefix' => false, 
            'omit_bots' => true,
        );


    @version 0.2
    @author Richard Cook <cook879@shoutwiki.com>
    @copyright Copyright © 2014 Richard Cook
    @license http://www.gnu.org/copyleft/gpl.html GNU General Public License 3.0 or later
"""


# User-defined variables
HOST = "irc.freenode.net"
IRC_PORT = 6667
#CHANNEL = "#ShoutWiki-staff" 
CHANNEL = "#cook879" # test channel
NICKNAME = "StaffWikiRC"
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

class StaffWikiBot( irc.IRCClient ):
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
        """ Processes messages

            Quits if operator private messages the bot 'quit'

            Responds appropriately to known triggers

            Links to revisions on Code Review

            Links to tickets in osTicket
        """
        
        if channel.lower() == self.nickname.lower():
            if re.search( IRC_OPERATOR, user ) or re.search( IRC_OPERATOR2, user ) or re.search( IRC_OPERATOR3, user ):
                if message.lower() == 'quit':
                    reactor.stop()
        elif channel.lower() == CHANNEL:
            # I'm sure there's more than 3 important pages :P
            if re.search( "^!private", message ):
                self.msg( CHANNEL, "Private wiki code: https://staff.shoutwiki.com/wiki/Private_wiki" )
            elif re.search( "^!social", message ):
                self.msg( CHANNEL, "Social tools: https://staff.shoutwiki.com/wiki/Social_tools" )
                self.msg( CHANNEL, "Social tools installation guide: https://staff.shoutwiki.com/wiki/KB:Installing_social_profile" )
            elif re.search( "^!targets", message ):
                self.msg( CHANNEL, "Our targets for the year: https://staff.shoutwiki.com/wiki/ShoutWiki_2014" )

            elif re.search( "r[0-9]+", message ):
                revisions = re.findall( "r[0-9]+", message )
                for revision in revisions:
                    rNo = revision[1:]
                    self.msg( CHANNEL, "https://staff.shoutwiki.com/wiki/Special:Code/ShoutWiki/" + rNo )

            elif re.search( "ticket #[0-9]+", message ):
                tickets = re.findall( "ticket #[0-9]+", message )
                for ticket in tickets:
                    tNo = ticket[8:]
                    self.msg( CHANNEL, "https://support.shoutwiki.com/scp/tickets.php?id=" + tNo )

            elif re.search( "bug #[0-9]+", message ):
                bugs = re.findall( "bug #[0-9]+", message)
                for bug in bugs:
                    bNo = bug[5:]
                    self.msg( CHANNEL, "https://bugzilla.shoutwiki.com/show_bug.cgi?id=" + bNo )
                
class StaffWikiBotFactory( protocol.ClientFactory ):
    """ Factory class inherits from ClientFactory
            see https://twistedmatrix.com/documents/14.0.0/api/twisted.internet.protocol.ClientFactory.html
    """

    def buildProtocol( self, addr ):
        b = StaffWikiBot()
        b.factory = self
        return b

    def clientConnectionLost( self, connector, reason ):
        """ If we get disconnected, try and reconnect to server. """
        connector.connect()

    def clientConnectionFailed( self, connector, reason ):
        print("Connection failed: ", reason)
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
f = StaffWikiBotFactory()

# UDP stuff
reactor.listenUDP( UDP_PORT, Echo() )

# Connect factory to host and port
reactor.connectTCP( HOST, IRC_PORT, f )

# Run bot
reactor.run()
