# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# rtcjazz/control/check_connection.py

import logging

from rqmjazz.core.RQMClient import RQMClient


def process(task_vars):
    conf = task_vars['configuration']

    # The configuration we get here is a delegate to an underlying java class.  This is
    # different than the 'server' we get defined in the synthetic.xml.  Convert it to
    # look like the 'server' object.
    server = {
        'url': conf._delegate.getUrl(), 
        'username': conf._delegate.getUsername(),
        'password': conf._delegate.getPassword(), 
        'authenticationMethod': conf._delegate.getAuthenticationMethod(), 
        'domain': conf._delegate.getDomain(), 
        'proxyHost': conf._delegate.getProxyHost(), 
        'proxyPort': conf._delegate.getProxyPort(), 
        'proxyUsername': conf._delegate.getProxyUsername(), 
        'proxyPassword': conf._delegate.getProxyPassword()
    }

    client = RQMClient.create_client(server, server["username"], server["password"])
    result = client.check_connection()

if __name__ == '__main__' or __name__ == '__builtin__':
    process(locals())
