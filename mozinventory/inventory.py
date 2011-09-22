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

import traceback
import sys
import urllib
import urllib2
import base64
import json
import pprint
 
class MozillaInventory(object):
    def __init__(self, username, password, url='https://inventory.mozilla.org/api/',
                    debug=False):
        self.username = username
        self.password = password
        self.request = None
        self.url = url
        self.debug = debug

    def get_data(self,data):
        try:
            data = urllib.urlencode(data)
        except:
            data = data
        return data

    #Read a system by either it's hostname from inventory or by it's id number
    #API Availability: v1
 
    def system_read(self, search):
            return self.create_request('system/%s/' % search, 'GET')
 
    #Returns a list of systems by pattern searching. Does not do true regex search.
    #API Availability: v2
 
    def system_hostname_search(self, search):
            return self.create_request('system/1/?name_search=%s' % search, 'GET')
 
    def system_create(self, hostname):
            return self.create_request('system/%s/' % hostname, 'POST')
 
    def system_delete(self, system_id):
            return self.create_request('system/%s/' % system_id, 'DELETE')
 
    def system_update(self, system_id, data):
            return self.create_request('system/%s/' % system_id, 'PUT', self.get_data(data))
 
    def network_adapter_create(self, system_id, data):
            return self.create_request('networkadapter/%s/' % system_id, 'POST', self.get_data(data))
 
    def network_adapter_update(self, network_adapter_id, data):
            return self.create_request('networkadapter/%s/' % network_adapter_id, 'PUT', self.get_data(data))
 
    def network_adapter_delete(self, network_adapter_id):
            return self.create_request('networkadapter/%s/' % network_adapter_id, 'DELETE')
 
    def keyvalue_search(self, data):
            return self.create_request('keyvalue/?%s' % self.get_data(data), 'GET')
 
    def keyvalue_create(self, keyvalue_id, data):
            return self.create_request('keyvalue/%s/' % keyvalue_id, 'POST', self.get_data(data))
 
    def keyvalue_read(self, keyvalue_id):
            return self.create_request('keyvalue/%s/' % keyvalue_id, 'GET')
 
    def keyvalue_update(self, keyvalue_id, data):
            return self.create_request('keyvalue/%s/' % keyvalue_id, 'PUT', self.get_data(data))
             
    def keyvalue_delete(self, keyvalue_id):
            return self.create_request('keyvalue/%s/' % keyvalue_id, 'DELETE')
 
    def delete_adapter(self, keyvalue_id, data):
            data['key_type'] = 'delete_network_adapter'
            data = self.get_data(data)
            return self.create_request('keyvalue/%s/?%s' % (keyvalue_id, data), 'DELETE')
 
    def delete_all_adapters(self, keyvalue_id, data):
            data['key_type'] = 'delete_all_network_adapters'
            data = self.get_data(data)
            return self.create_request('keyvalue/%s/?%s' % (keyvalue_id, data), 'DELETE')

    def create_request(self, url, method='GET', data = None):
        request = urllib2.Request(self.url + url, data)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        if self.debug:
            print "Authorization: Basic", base64string
        request.add_header("Authorization", "Basic %s" % base64string)  

        if self.debug:
            print "%s %s" % (method, self.url + url)
            if data:
                pprint.pprint(data)
        request.get_method = lambda: method

        result = {'success':False}
        try:
            result_string = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            if self.debug:
                print "ERROR:"
                traceback.print_exc()
            return {"success": False, "status_code":str(e.code), "error": e}

        if self.debug:
            print "RESULT:"
            print result_string

        # try to strip off a leading JSONP header
        try:
            result_string = result_string.split("= ")[1]
        except:
            pass

        result['data'] = json.loads(result_string)
        if result['data'] is None:
            result['success'] = False
        elif len(result['data']) is 0:
            result['success'] = False
        else:
            result['success'] = True
        return result
