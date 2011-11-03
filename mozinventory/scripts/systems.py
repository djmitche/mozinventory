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
import csv
import argparse
from mozinventory.scripts import util, base

class SystemMixin(object):

    system_columns = [
        'hostname',
        'serial',
        'asset_tag',
        'rack_order',
        'patch_panel_port',
        'oob_ip',
        'switch_ports',
        'oob_switch_ports',
        'notes',
    ]

    def add_display_opts(self, parser):
        group = parser.add_argument_group('output format arguments')

        mutex = group.add_mutually_exclusive_group()

        mutex.add_argument('--csv', dest='output_fn', action='store_const', 
                const=SystemMixin.display_csv,
                help='Produce output in CSV format')

        mutex.add_argument('--human', dest='output_fn', action='store_const', 
                const=SystemMixin.display_human,
                help='Produce output in human-readable format (default)')

        mutex.add_argument('--names', dest='output_fn', action='store_const', 
                const=SystemMixin.display_names,
                help='Output a newline-separated list of hostnames, suitable for xargs')

        group.add_argument('--no-header', dest='output_no_header', action='store_true',
                help='Do not output a header (with --csv)')

        default_fields = ','.join(self.system_columns)
        group.add_argument('--fields', dest='output_fields',
                default=default_fields,
                help='comma-separated list of fields to display; default is %s'
                                % default_fields)


    def display_hosts(self, hosts):
        return (self.opts.output_fn or SystemMixin.display_human)(self, hosts)


    def display_csv(self, hosts):
        fields = self.opts.output_fields.split(',')
        if self.opts.output_no_header:
            writer = csv.writer(sys.stdout)

            for host in hosts:
                writer.writerow(tuple(host[f] for f in fields))
        else:
            writer = csv.DictWriter(sys.stdout, fields)

            # header row
            writer.writerow(dict((f, f) for f in fields))
            for host in hosts:
                writer.writerow(dict((f, host.get(f, '')) for f in fields))


    def display_human(self, hosts):
        fields = self.opts.output_fields.split(',')
        max_field = max(len(f) for f in fields)
        for host in hosts:
            print host['hostname']
            for key in fields:
                if key == 'hostname': continue
                if key in host and host[key]:
                    print "  %-*s: %s" % (max_field, key, host[key])


    def display_names(self, hosts):
        for host in hosts:
            print host['hostname']



class Get(base.Subcommand, SystemMixin):

    oneline = "Get information about a system, specified by hostname"

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.oneline,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('hostname',
                help="hostname to get information for")

        self.add_display_opts(parser)

        return parser

    def run(self, inv):
        rv = inv.system_read(self.opts.hostname)
        util.handle_error(rv)

        self.display_hosts([ rv['data'] ])


class Search(base.Subcommand, SystemMixin):

    oneline = "Get information about multiple systems"

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.oneline,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('--hostname-fragment', dest='hostname_fragment', default=None,
                help="a fragment of the hostname (substring match)")
                
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

        self.add_display_opts(parser)

        return parser


    def process_options(self):
        if not self.opts.asset_tag and \
           not self.opts.oob_ip and \
           not self.opts.serial and \
           not self.opts.system_rack_id and \
           not self.opts.rack_order and \
           not self.opts.hostname_fragment:
            self.opts.error("a search criterion is required")


    def run(self, inv):
        criteria = {}
        use_search = False
        if self.opts.asset_tag:
            use_search = True
            criteria['asset_tag'] = self.opts.asset_tag

        if self.opts.serial:
            use_search = True
            criteria['serial'] = self.opts.serial

        if self.opts.system_rack_id:
            use_search = True
            criteria['system_rack_id'] = self.opts.system_rack_id

        if self.opts.rack_order:
            use_search = True
            criteria['rack_order'] = self.opts.rack_order

        if self.opts.oob_ip:
            use_search = True
            criteria['oob_ip'] = self.opts.oob_ip

        if use_search:
            rv = inv.system_search(criteria)
        else:
            rv = inv.system_hostname_search(self.opts.hostname_fragment)

        util.handle_error(rv)

        data = rv['data']

        # if we used system_search, but had a hostname fragment, filter
        # that client-side
        if use_search and self.opts.hostname_fragment:
            frag = self.opts.hostname_fragment
            data = [ h for h in data if frag in h['hostname'] ]

        if not data:
            print >>sys.stderr, "not found."
            sys.exit(1)

        self.display_hosts(data)


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
