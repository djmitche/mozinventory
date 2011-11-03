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

import mock
import textwrap
import nose.tools
from mozinventory.scripts import systems
from mozinventory.test.scripts import util

host_data = {
    'allocation': {
        '_state': '<django.db.models.base.ModelState object at 0xc266c2c>',
        'id': 2,
        'name': 'release',
    },
    'asset_tag': '113075',
    'change_password': None,
    'created_on': None,
    'hostname': 'somehost',
    'id': 1460,
    'is_dhcp_server': 0,
    'is_dns_server': 0,
    'is_nagios_server': 0,
    'is_puppet_server': 1,
    'is_switch': 0,
    'licenses': '',
    'notes': '',
    'oob_ip': '1.1.9.37',
    'oob_switch_port': '',
    'operating_system': None,
    'patch_panel_port': '',
    'purchase_date': '2009-10-10',
    'purchase_price': '$32.56',
    'rack_order': '25.03',
    'ram': '',
    'releng_bitlength': None,
    'releng_datacenter': None,
    'releng_distro': None,
    'releng_environment': None,
    'releng_purpose': None,
    'releng_role': None,
    'releng_trustlevel': None,
    'serial': 'lkajsdfliG5',
    'server_model': {
        '_state': '<django.db.models.base.ModelState object at 0xc266fac>',
        'description': 'MAC MIN 2.26/2x1G/160/SD/AP/BT - USA',
        'id': 241,
        'model': 'Mac Mini - r3',
        'part_number': ' MC238LL/A',
        'vendor': 'Apple',
    },
    'switch_ports': 'sw-8a.scl1:23',
    'system_rack': {
        'id': 89,
        'location': {'id': 13, 'name': 'SCL1'},
        'name': '101-08',
    },
    'system_status': None,
    'updated_on': None,
}

host2_data = host_data.copy()
host2_data['hostname'] = 'otherhost'
host2_data['asset_tag'] = '9359393'


class test_Add(util.ScriptTestCase):

    subcommand_class = systems.Add

    def test_simple(self):
        self.inv.system_create.return_value = (
                dict(success=True, data=dict(id=298)))
        self.inv.system_update.return_value = (
                dict(success=True))
        self.run_script('add', 'mynewhost')
        self.inv.system_create.assert_called_with('mynewhost')
        self.inv.system_update.assert_called_with(298, {})

    def test_args(self):
        self.inv.system_create.return_value = (
                dict(success=True, data=dict(id=298)))
        self.inv.system_update.return_value = (
                dict(success=True))
        self.run_script('add', 'mynewhost',
                '--serial', '1234',
                '--asset-tag', '60000',
                '--location', 'portugal',
                '--oob-ip', '127.0.0.1',
                '--notes', 'note this!')
        self.inv.system_create.assert_called_with('mynewhost')
        self.inv.system_update.assert_called_with(298,
                dict(serial='1234', asset_tag='60000', location='portugal',
                     oob_ip='127.0.0.1', notes='note this!'))

    def test_fail_create(self):
        self.inv.system_create.return_value = (
                dict(success=False, status_code='404'))

        with mock.patch('mozinventory.scripts.util.handle_error') as handle_error:
            handle_error.side_effect = SystemExit
            self.assertRaises(SystemExit, lambda :
                self.run_script('add', 'mynewhost'))

        self.inv.system_create.assert_called_with('mynewhost')


class test(util.ScriptTestCase):

    subcommand_class = systems.Get

    def test_simple(self):
        self.inv.system_read.return_value = (
                dict(success=True, data=host_data))
        stdout = []
        with util.capture_stdout(stdout):
            self.run_script('get', 'somehost')
        stdout = ''.join(stdout).strip()

        self.inv.system_read.assert_called_with('somehost')
        nose.tools.eq_(stdout, textwrap.dedent("""\
                -- somehost --
                asset_tag=113075
                oob_ip=1.1.9.37
                rack_order=25.03
                serial=lkajsdfliG5
                switch_ports=sw-8a.scl1:23""").strip())
