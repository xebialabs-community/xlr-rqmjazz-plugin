#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys, os
from unittest import TestCase
from mock import patch, Mock, MagicMock

# include source in path so test can find it
testdir = os.path.dirname(__file__)
srcdir = '../main/resources'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

class TestExecute(TestCase):
    task_vars = {
        'server': {
            'url': 'http://localhost:8088',
            'username': 'tester',
            'password': 'password'
        },
        'polling_interval': 300,
        'client_timeout': 1080,
        'consider_execution_result': False,
        'test_configuration': 'xxx'
    }

    def test_successful_simple_test(self):
        self.task_vars['test_configuration'] = 'pass'
        test_output, test_results, test_failures = execute_test.process(self.task_vars)

        self.assertEqual(test_results, 'pass')
        self.assertEqual(len(test_failures), 0)


    def test_successful_multi_test(self):
        self.task_vars['test_configuration'] = 'pass-2'
        test_output, test_results, test_failures = execute_test.process(self.task_vars)

        self.assertEqual(test_results, 'pass')
        self.assertEqual(len(test_failures), 0)


    def test_failed_test(self):
        self.task_vars['test_configuration'] = 'fail'
        test_output, test_results, test_failures = execute_test.process(self.task_vars)

        self.assertEqual(test_results, 'fail')
        self.assertEqual(len(test_failures), 5)
        self.assertTrue('JSON Example.Object' in test_failures)
        self.assertTrue('JSON Example.Boolean' in test_failures)
        self.assertTrue('JSON Example.Multiple values' in test_failures)
        self.assertTrue('JSON Example.Empty array' in test_failures)
        self.assertTrue('JSON Example.Full array' in test_failures)
