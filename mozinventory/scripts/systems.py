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
import argparse
from mozinventory.scripts import util, base


class Get(base.Subcommand):

    oneline = "Get information about a system, specified by hostname"

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.oneline,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('hostname',
                help="hostname to get information for")

        return parser

    def run(self, inv):
        rv = inv.system_read(self.opts.hostname)
        util.handle_error(rv)

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


class Search(base.Subcommand):

    oneline = "Get information about multiple systems"

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.oneline,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('--asset-tag', dest='asset_tag', default=None,
                help="asset tag number of system")
                
        parser.add_argument('--serial', dest='serial', default=None,
                help="serial number of system")

        parser.add_argument('--oob-ip', dest='oob_ip', default=None,
                help="oob ip address of system")

        parser.add_argument('--system-rack-id', dest='system_rack_id', default=None,
                help="system_rack_id of system")

        parser.add_argument('--rack-order', dest='rack_order', default=None,
                help="rack_order of system")
        return parser


    def process_options(self):
        if not self.opts.asset_tag and \
           not self.opts.oob_ip and \
           not self.opts.serial and \
           not self.opts.system_rack_id and \
           not self.opts.rack_order:
            self.error("a search criterion is required")


    def run(self, inv):
        criteria = {}
        has_search = False
        if self.opts.asset_tag:
            has_search = True
            criteria['asset_tag'] = self.opts.asset_tag

        if self.opts.serial:
            has_search = True
            criteria['serial'] = self.opts.serial

        if self.opts.system_rack_id:
            has_search = True
            criteria['system_rack_id'] = self.opts.system_rack_id

        if self.opts.rack_order:
            has_search = True
            criteria['rack_order'] = self.opts.rack_order

        if self.opts.oob_ip:
            has_search = True
            criteria['oob_ip'] = self.opts.oob_ip

        if has_search:
            rv = inv.system_search(criteria)

        util.handle_error(rv)

        if has_search:
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


class Add(base.Subcommand):

    oneline = "Add a new system to inventory"

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.oneline,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('hostname',
                help="hostname of new host")

        parser.add_argument('--serial', dest='serial', default=None,
                help="serial number")

        parser.add_argument('--asset-tag', dest='asset_tag', default=None,
                help="asset tag")

        parser.add_argument('--location', dest='location', default=None,
                help="system location")

        parser.add_argument('--oob-ip', dest='oob_ip', default=None,
                help="out-of-band management IP")

        parser.add_argument('--notes', dest='notes', default=None,
                help="free-form host notes")

        return parser

    def run(self, inv):
        rv = inv.system_create(self.opts.hostname)
        util.handle_error(rv)

        id = rv['data']['id']
        data = {}
        for k in 'serial asset_tag location oob_ip notes'.split():
            if hasattr(self.opts, k) and getattr(self.opts, k) is not None:
                data[k] = getattr(self.opts, k)
        rv = inv.system_update(id, data)
        util.handle_error(rv)

        print "Created; system ID is %d" % (id,)
