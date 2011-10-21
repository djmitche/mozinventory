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

import argparse
from mozinventory.scripts import util, base

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
