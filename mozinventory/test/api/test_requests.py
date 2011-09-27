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

import urllib2
from mozinventory import inventory
from mozinventory.test.api.util import patch_urllib2

inv = inventory.MozillaInventory('me', 'pw', 'http://x/')

@patch_urllib2([ ('GET', 'http://x/foo/bar', None, '{ "x": 1 }', None), ])
def test_simple_get():
    rv = inv.create_request('foo/bar')
    assert rv == dict(success=True, data=dict(x=1))

@patch_urllib2([ ('GET', 'http://x/y/foo/bar', None, '{ "x": 1 }', None), ])
def test_simple_get_no_trailing_slash():
    inv = inventory.MozillaInventory('me', 'pw', 'http://x/y')
    rv = inv.create_request('foo/bar')
    assert rv == dict(success=True, data=dict(x=1))

# a 'null' response is handled specially
@patch_urllib2([ ('GET', 'http://x/foo/bar', None, 'null', None), ])
def test_null_get():
    rv = inv.create_request('foo/bar')
    assert rv == dict(success=False, data=None)

# JSON of an empty string is handled specially
@patch_urllib2([ ('GET', 'http://x/foo/bar', None, '""', None), ])
def test_empty_string_get():
    rv = inv.create_request('foo/bar')
    assert rv == dict(success=False, data='')

# JSONP responses are handled, too
@patch_urllib2([ ('GET', 'http://x/foo/bar', None, 'foo = "bar"', None), ])
def test_jsonp_get():
    rv = inv.create_request('foo/bar')
    assert rv == dict(success=True, data='bar')

# Invalid responses should return success=False
@patch_urllib2([ ('GET', 'http://x/foo/bar', None, '{x{', None), ])
def test_invalid_json():
    rv = inv.create_request('foo/bar')
    assert rv['success'] == False
    assert rv['status_code'] == '999'
    assert type(rv['error']) == ValueError

# Invalid responses should return success=False
@patch_urllib2([
    ('GET', 'http://x/foo/bar', None, '',
        urllib2.HTTPError('http://x/foo/bar', '555', 'Oh Noes', 'hdr', None)),
])
def test_http_exception():
    rv = inv.create_request('foo/bar')
    assert rv['success'] == False
    assert rv['status_code'] == '555'
    assert type(rv['error']) == urllib2.HTTPError
