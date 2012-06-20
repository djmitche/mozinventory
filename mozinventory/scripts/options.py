# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
# 
# The Original Code is mozinventory
#
# The Initial Developer of the Original Code is Rob Tucker.  Portions created
# by Rob Tucker are Copyright (C) Mozilla, Inc. All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms of the
# GNU Public License, Version 2 (the  "GPLv2 License"), in which case the
# provisions of GPLv2 License are applicable instead of those above. If you
# wish to allow use of your version of this file only under the terms of the
# GPLv2 License and not to allow others to use your version of this file under
# the MPL, indicate your decision by deleting the provisions above and replace
# them with the notice and other provisions required by the GPLv2 License. If
# you do not delete the provisions above, a recipient may use your version of
# this file under either the MPL or the GPLv2 License.

import os
import sys
import argparse
import textwrap
import ConfigParser

subcommands = {

    # systems
    'get' : 'mozinventory.scripts.systems.Get',
    'search' : 'mozinventory.scripts.systems.Search',
    'add' : 'mozinventory.scripts.systems.Add',

    'systemrack-get' : 'mozinventory.scripts.systemracks.Get',
}

class Options(argparse.Namespace):


    config_help = textwrap.dedent("""\
    Configuration is in ~/.mozinventoryrc.  This file must have mode 0700.  It is
    an ini-style file supporting the following arguments:

        [api]
        url - the base API URL

        [auth]
        username - for Mozilla, the long LDAP form
        password - password for username

        [debug]
        api - set to '1' to debug the inventory API interface
    """)

    description = textwrap.dedent("""\
    An interface to the Mozilla inventory tool.

    This utility requires access to a compatible inventory server, and a username
    and password. 
    """)

    def __init__(self):
        super(Options, self).__init__()

        self.cmdline = []
        self.prog = 'mozinventory'

        # default values
        self.apiurl = 'https://inventory.mozilla.org/api/'
        self.password = None
        self.username = None
        self.debug = False


    def parse_config(self):
        """
        Parse the mozinventory configuration file.
        """

        cfgfile = os.path.expanduser("~/.mozinventoryrc")

        # check perms, since this might contain a password
        if os.path.exists(cfgfile):
            st = os.stat(cfgfile)
            if st.st_mode & 077:
                print >>sys.stderr, "WARNING: %s has unsafe permissions!" % cfgfile
                sys.exit(1)

        cfg = ConfigParser.RawConfigParser()
        cfg.read([cfgfile])
        if cfg.has_option('auth', 'password'):
            self.password = cfg.get('auth', 'password')

        if cfg.has_option('auth', 'username'):
            self.username = cfg.get('auth', 'username')

        if cfg.has_option('debug', 'api'):
            self.debug = True

        if cfg.has_option('abi', 'url'):
            self.apiurl = cfg.get('api', 'url')


    def parse_global_options(self, cmdline):
        """
        Parse global options out of the cmdline passed to the constructor,
        leaving any unparsed arguments for later
        """

        parser = self.parser = argparse.ArgumentParser(
                description=self.description,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                add_help=False)
        self.prog = parser.prog

        parser.add_argument('-A', '--api', dest='apiurl',
                help="""URL of the inventory API""")

        parser.add_argument('-U', '--username', dest='username',
                help="""LDAP Username (long)""")

        parser.add_argument('--debug', dest='debug',
                action='store_true',
                help="print debugging information")

        parser.add_argument('--help', dest='help',
                help="get help on a particular command")

        parser.add_argument('--help-commands', dest='help_commands',
                action='store_true',
                help="describe available commands")

        # parse the args
        _, self.cmdline = parser.parse_known_args(cmdline, namespace=self)

        # handle help
        if self.help_commands:
            self.show_subcommands()
        elif self.help:
            self.show_help(self.help)


    def parse_subcommand(self):
        """
        Parse a subcommand from the command line, up until any unrecognized
        arguments.

        @returns: a Subcommand instance, or None if there is no subcommand
        """

        if not self.cmdline:
            return None

        if self.cmdline[0] not in subcommands:
            self.error("No such subcommand '%s'" % (self.cmdline[0],))
        subcommand_name = self.cmdline.pop(0)

        cls = self.get_object(subcommands[subcommand_name])
        subcommand = cls(subcommand_name, self)

        parser = subcommand.get_parser()
        parser.prog = '%s %s' % (self.prog, subcommand_name)
        parser.parse_args(self.cmdline, namespace=self)
        subcommand.process_options()

        return subcommand


    def show_help(self, subcommand_name=None):
        if subcommand_name:
            if subcommand_name not in subcommands:
                self.error("no such subcommand '%s'" % subcommand_name)
            cls = self.get_object(subcommands[subcommand_name])
            subcommand = cls(subcommand_name, self)
            parser = subcommand.get_parser()
            parser.prog = '%s %s' % (self.prog, subcommand_name)
            parser.print_help()
            self.parser.exit(1)
        else:
            self.parser.print_help()
            print ""
            self.show_subcommands()


    def show_subcommands(self):
        names = sorted(subcommands.keys())
        descriptions = []
        for n in names:
            cls = self.get_object(subcommands[n])
            subcommand = cls(n, self)
            descriptions.append((n, subcommand.oneline))

        max_name = max(len(n) for n in names)
        print self.config_help
        print ""
        print "Available subcommands:\n"
        for n, d in descriptions:
            print "%s %-*s - %s" % (self.prog, max_name, n, d)
        print ""
        print "Use %s --help=<subcommand> for subcommand help" % (self.prog)
        self.parser.exit(1)


    def error(self, *args):
        self.parser.error(*args)


    def get_object(self, name):
        # import the module
        name = name.split('.')
        module_name = ".".join(name[:-1])
        module = __import__(module_name)

        # traverse from the top level to the actual module
        for pkg in name[1:-1]:
            module = getattr(module, pkg)
        return getattr(module, name[-1])


