# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

import fixtures
import mock
from oslo_config import cfg
from oslo_log import log
from oslotest import base
import testscenarios

from datahub.common import context as dh_context
from datahub.tests import conf_fixture

CONF = cfg.CONF
try:
    log.register_options(CONF)
except cfg.ArgsAlreadyParsedError:
    pass
CONF.set_override('use_stderr', False)


class BaseTestCase(testscenarios.WithScenarios, base.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.addCleanup(cfg.CONF.reset)


class TestCase(base.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.context = dh_context.RequestContext(user='fake_user')

        def make_context(*args, **kwargs):
            if not kwargs.get('user_id'):
                kwargs['user_id'] = 'fake_user'

            context = dh_context.RequestContext(*args, **kwargs)
            return dh_context.RequestContext.from_dict(context.to_dict())

        p = mock.patch.object(dh_context, 'make_context',
                              side_effect=make_context)
        self.mock_make_context = p.start()
        self.addCleanup(p.stop)

        self.useFixture(conf_fixture.ConfFixture())
        self.useFixture(fixtures.NestedTempfile())

    def config(self, **kw):
        """Override config options for a test."""
        group = kw.pop('group', None)
        for k, v in kw.items():
            CONF.set_override(k, v, group)

    def get_path(self, project_file=None):
        """Get the absolute path to a file. Used for testing the API.

        :param project_file: File whose path to return. Default: None.
        :returns: path to the specified file, or path to project root.
        """
        root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..',
                                            '..',
                                            )
                               )
        if project_file:
            return os.path.join(root, project_file)
        else:
            return root
