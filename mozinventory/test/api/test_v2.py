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

from mozinventory import inventory
from mozinventory.test.api.util import patch_create_request
import nose.tools

inv = inventory.MozillaInventory('me', 'pw', 'http://x/')

@patch_create_request
def test_system_hostname_search(requests):
    assert inv.system_hostname_search('foo') == "request-1"
    nose.tools.eq_(requests, [
        ( 'GET', 'v2/system/1/?name_search=foo'),
    ])

@patch_create_request
def test_system_create(requests):
    assert inv.system_create('foo') == "request-1"
    nose.tools.eq_(requests, [
        ( 'POST', 'v2/system/foo/'),
    ])

@patch_create_request
def test_system_delete(requests):
    assert inv.system_delete(12) == "request-1"
    nose.tools.eq_(requests, [
        ( 'DELETE', 'v2/system/12/'),
    ])

@patch_create_request
def test_system_update(requests):
    assert inv.system_update(12, dict(a='b', x='y')) == "request-1"
    nose.tools.eq_(requests, [
        ( 'PUT', 'v2/system/12/', 'a=b&x=y'),
    ])

@patch_create_request
def test_network_adapter_create(requests):
    assert inv.network_adapter_create(12, dict(a='b', x='y')) == "request-1"
    nose.tools.eq_(requests, [
        ( 'POST', 'v2/networkadapter/12/', 'a=b&x=y'),
    ])

@patch_create_request
def test_network_adapter_delete(requests):
    assert inv.network_adapter_delete(12) == "request-1"
    nose.tools.eq_(requests, [
        ( 'DELETE', 'v2/networkadapter/12/'),
    ])

@patch_create_request
def test_network_adapter_update(requests):
    assert inv.network_adapter_update(12, dict(a='b', x='y')) == "request-1"
    nose.tools.eq_(requests, [
        ( 'PUT', 'v2/networkadapter/12/', 'a=b&x=y'),
    ])

# TODO: remainder of v2 tests
