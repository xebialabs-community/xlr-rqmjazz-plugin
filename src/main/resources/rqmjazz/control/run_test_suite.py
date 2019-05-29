# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging

from rqmjazz.core.RQMClient import RQMClient

logging.basicConfig(filename='log/plugin.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger('run_test_suite')

def process(task_vars):
    server = task_vars['server']

    logger.debug('task_vars: %s' % task_vars)

    client = RQMClient.create_client(server, username = task_vars["username"], password = task_vars["password"])
    
    return client.run_test_suite(task_vars['project_area'], task_vars['tser_id'])

if __name__ == '__main__' or __name__ == '__builtin__':
    result_url = process(locals())
