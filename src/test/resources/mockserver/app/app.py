#!flask/bin/python

# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from flask import Flask
from flask import request, Response
from flask import make_response
from functools import wraps
import os, io, json

app = Flask(__name__)

def getFile( fileName, status="200" ):
    filePath = "/mockserver/responses/%s" % fileName
    if not os.path.isfile(filePath):
        raise AuthError({"code": "response_file_not_found", "description": "Unable to load response file"}, 500)

    f = io.open(filePath, "r", encoding="utf-8")

    resp = make_response( (f.read(), status) )

    if fileName.endswith('.json'):
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    elif fileName.endswith('.xml'):
        resp.headers['Content-Type'] = 'application/xml; charset=utf-8'

    return resp

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'xlr_test' and password == 'admin'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """
    Determines if the basic auth is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return "Hello, from Mock Server!"


@app.route('/qm/service/com.ibm.rqm.common.service.rest.IOptionRestService/j_security_check', methods=['POST'])
def doLogin():
    # print('Type: %s' % type(request))
    # print('Vars: %s' % vars(request))
    # print('Dir:  %s' % dir(request))
    # print('Request ------\n')
    # print(request)
    print('Data: %s' % request.get_data())

    resp = make_response('ok', 200)
    resp.set_cookie('rqmcookie', 'I am cookie')
    return resp


@app.route('/qm/rootservices', methods=['GET'])
@requires_auth
def getQmRootServices():
    return getFile("qm_rootservices.xml")


@app.route('/qm/oslc_qm/catalog', methods=['GET'])
def getQmCatalog():
    return getFile("qm_catalog.xml")


@app.route('/service/com.ibm.rqm.execution.common.service.rest.ITestcaseExecutionRecordRestService/executeDTO', methods=['POST'])
def runTest():
    resp = make_response( ("ok", 200) )
    resp.headers['Content-Location'] = '/somewhere/special'
    return resp


@app.route('/somewhere/special', methods=['GET'])
def getResults():
    return getFile("qm_executionresult.xml")


if __name__ == '__main__':
    app.run(debug=True)
