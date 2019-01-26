# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from rqmjazz.core.RQMClient import RQMClient

def process(task_vars):
    server = task_vars['server']

    credentials = CredentialsFallback(server, task_vars['username'], task_vars['password']).getCredentials()
    client = RQMClient.createClient(server, credentials["username"], credentials["password"])
    
    return client.run_test_suite(task_vars['project_area'], task_vars['tser_id'])

if __name__ == '__main__' or __name__ == '__builtin__':
    process(locals())
