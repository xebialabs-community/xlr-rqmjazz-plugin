# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from rqmjazz.core.RQMClient import RQMClient

def process(task_vars):
    server = task_vars['server']

    credentials = CredentialsFallback(task_vars['rqmServer'], task_vars['username'], task_vars['password']).getCredentials()
    client = RQMClient.createClient(server, credentials["username"], credentials["password"])

    return client.get_test_results(task_vars['result_url'])

if __name__ == '__main__' or __name__ == '__builtin__':
    process(locals())
