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

import ConfigParser
import sys
import os
import getpass
import argparse
from mozinventory.inventory import MozillaInventory

subcommands = []

from mozinventory.scripts import get, add, systemrack_get, search
subcommands.extend([ get, add, systemrack_get, search])


def parse_config(args):
    cfgfile = os.path.expanduser("~/.mozinventoryrc")

    # check perms, since this might contain a password
    if os.path.exists(cfgfile):
        st = os.stat(cfgfile)
        if st.st_mode & 077:
            print >>sys.stderr, "WARNING: %s has unsafe permissions!" % cfgfile
            sys.exit(1)

    args.password = ''

    cfg = ConfigParser.RawConfigParser()
    cfg.read([cfgfile])
    if cfg.has_option('auth', 'password'):
        args.password = cfg.get('auth', 'password')

    if cfg.has_option('auth', 'username') and not args.username:
        args.username = cfg.get('auth', 'username')

    if cfg.has_option('debug', 'api') and not args.debug:
        args.debug = True

description = """\
An interface to the Mozilla inventory tool.

This utility requires access to a compatible inventory server, and a username
and password. 

Configuration is in ~/.mozinventoryrc.  This file must have mode 0700.  It is
an ini-style file supporting the following arguments:

    [auth]
    username - for Mozilla, the long LDAP form
    password - password for username

    [debug]
    api - set to '1' to debug the inventory API interface

Use `%(prog)s command --help` to see help for the subcommands shown below.
"""

def parse_options():
    parser = argparse.ArgumentParser(description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.set_defaults(_module=None)

    parser.add_argument('-A', '--api', dest='apiurl',
            default='https://inventory.mozilla.org/api/',
            help="""URL of the inventory API""")

    parser.add_argument('-U', '--username', dest='username',
            default='',
            help="""LDAP Username (long)""")

    parser.add_argument('--debug', dest='debug',
            default=False, action='store_true',
            help="print debugging information")

    subparsers = parser.add_subparsers(title='subcommands')

    for module in subcommands:
        subparser = module.setup_argparse(subparsers)
        subparser.set_defaults(module=module, subparser=subparser)

    # parse the args
    args = parser.parse_args()

    # make sure we got a subcommand
    if not args.module:
        parser.error("No subcommand specified")

    # parse the configs
    parse_config(args)

    # ensure we have a password
    if not args.password:
        args.password = getpass.getpass("LDAP Password for %s: " % args.username)

    # let it process its own args
    args.module.process_args(args.subparser, args)

    # and return the results
    return args.module.main, args

def main():
    func, args = parse_options()
    inv = MozillaInventory(args.username, args.password, args.apiurl, debug=args.debug)

    # for now, this raises exceptions for errors
    func(inv, args)

if __name__ == '__main__':
    main()
