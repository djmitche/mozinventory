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
import nose.tools

def patch_urllib2(expectations, exp_auth='bWU6cHc='):
    """
    A decorator to patch urllib2 to expect the requests in `expectations`, and
    to provide the given responses.  The argument is a list of tuples,
    `(method, url, rq_data, resp_data, raises)` where `url` is the URL to
    expect with method `method`, `rq_data` is the data to expect with that URL
    (or None), `resp_data` is the data to return, and `raises` is an exception
    instance that should be raised from `urlopen()`.

    The base64 data in the authorization header is given by `exp_auth`.  The
    default value is a hash of 'me', password 'pw'.
    """
    def dec(fn):
        @nose.tools.make_decorator(fn)
        def wrap(*args, **kwargs):
            local_expectations = expectations[:]
            state = {}
            def patched_Request(url, data):
                assert local_expectations
                nose.tools.eq_(url, local_expectations[0][1])
                nose.tools.eq_(data, local_expectations[0][2])
                rq = mock.Mock(name="Request-%s" % (url,))
                state['last_rq'] = rq
                return rq

            def patched_urlopen(rq):
                # check that we got the request that was just made
                assert rq is state['last_rq']

                nose.tools.eq_(rq.get_method(), expectations[0][0])
                rq.add_header.assert_called_with('Authorization',
                        'Basic ' + exp_auth)

                del state['last_rq']

                exp = local_expectations.pop(0)
                if exp[4]:
                    raise exp[4]

                # make a file-like response object
                resp = mock.Mock(name='Response')
                resp.read.return_value = exp[3]
                return resp

            with mock.patch("urllib2.Request") as Request:
                Request.side_effect = patched_Request
                with mock.patch("urllib2.urlopen") as urlopen:
                    urlopen.side_effect = patched_urlopen

                    rv = fn(*args, **kwargs)
                    nose.tools.eq_([], local_expectations)
                    return rv
        return wrap
    return dec

def patch_create_request(fn):
    @nose.tools.make_decorator(fn)
    def wrap(*args, **kwargs):
        with mock.patch('mozinventory.inventory.MozillaInventory.create_request') as cr:
            requests = []
            def create_request(url, method='GET', data = None):
                if data:
                    requests.append((method, url, data))
                else:
                    requests.append((method, url))
                return "request-%d" % len(requests)
            cr.side_effect = create_request
            return fn(requests, *args, **kwargs)
    return wrap
