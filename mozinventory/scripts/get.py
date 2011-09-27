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
from mozinventory.scripts import util

def setup_argparse(subparsers):
    subparser = subparsers.add_parser('get', help='get information about host')

    subparser.add_argument('hostname',
            help="hostname to get information for")

    subparser.add_argument('--search', dest='search',
            default=False, action='store_true',
            help="search for hosts containing the hostname as a substring")

    return subparser

def process_args(subparser, args):
    if not args.hostname:
        subparser.error("a hostname is required")

def main(inv, args):
    if args.search:
        rv = inv.system_hostname_search(args.hostname)
    else:
        rv = inv.system_read(args.hostname)

    util.handle_error(rv)

    if args.search:
        data = rv['data']
        if not data:
            print >>sys.stderr, "not found."
            sys.exit(1)
    else:
        data = [ rv['data'] ]

    keys = dict(
        serial = 'serial',
        asset_tag = 'asset_tag',
        rack_order = 'rack_order',
        patch_panel_port = 'patch_panel_port',
        oob_ip = 'oob_ip',
        #allocation = 'allocation', -- bug 688627
        switch_ports = 'switch_ports',
        oob_switch_port = 'oob_switch_port',
        notes = 'notes',
    )
    for host in data:
        print "-- %s --" % host['hostname']
        for key, name in sorted(keys.items()):
            if key in host and host[key]:
                print "%s=%s" % (name, host[key])
