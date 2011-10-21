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
import unittest
import contextlib
from mozinventory.scripts import options

class ScriptTestCase(unittest.TestCase):

    def setUp(self):
        self.opts = options.Options()
        self.inv = mock.Mock(name="MozillaInventory")

    def run_script(self, *args):
        self.opts.cmdline = list(args)
        subcommand = self.opts.parse_subcommand()
        subcommand.run(self.inv)

@contextlib.contextmanager
def capture_stdout(dest):
    """
    Called as a context manager, this will capture stdout into a list named
    'dest' -- at least the data written by `sys.stdout.write()`.
    """
    dest[:] = []
    with mock.patch('sys.stdout.write') as write:
        def keep(s):
            dest.append(s)
        write.side_effect = keep

        # do the body of the with statement
        yield
