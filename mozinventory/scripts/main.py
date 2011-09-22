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

import sys
import os
import getpass
import argparse
from mozinventory.inventory import MozillaInventory

# subcommands
from mozinventory.scripts import get
subcommands = [ get ]

def get_password(args):
    pwfile = os.path.expanduser("~/.mozinventory-password")
    if os.path.exists(pwfile):
        st = os.stat(pwfile)
        if st.st_mode & 077:
            print >>sys.stderr, "WARNING: %s has unsafe permissions!" % pwfile
            sys.exit(1)
        return open(pwfile).read().strip()

    getpass.getpass("LDAP Password for %s: " % args.username)

description = """\
Runs mozinventory subcommands.

This requires access to a compatible inventory server, and a username and
password.  The password can be put in ~/.mozinventory-password, with
permissions 0700.  If this file is not present, then the command will prompt
for a password on every execution.
"""

def parse_options():
    parser = argparse.ArgumentParser(description=description)
    parser.set_defaults(_module=None)

    parser.add_argument('-A', '--api', dest='apiurl',
            default='http://inventory.mozilla.org/api/',
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

    # let it process its own args
    args.module.process_args(args.subparser, args)

    # assuming no errors yet, let's get a password
    args.password = get_password(args)

    # and return the results
    return args.module.main, args

def main():
    func, args = parse_options()
    inv = MozillaInventory(args.username, args.password, args.apiurl, debug=args.debug)

    # for now, this raises exceptions for errors
    func(inv, args)
