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


@app.route('/qm/rootservices', methods=['GET'])
@requires_auth
def getQmRootServices():
    return getFile("qm_rootservices.xml")


@app.route('/qm/oslc_qm/catalog', methods=['GET'])
def getQmCatalog():
    return getFile("qm_catalog.xml")





# from RTC, reference only
@app.route('/ccm/oslc/workitems/<workitem_id>', methods=['GET'])
@requires_auth
def getCcmWorkitem(workitem_id):
    return getFile("ccm_workitem.json")


@app.route('/ccm/oslc/workitems/<workitem_id>/rtc_cm:comments', methods=['GET'])
@requires_auth
def getCcmWorkitemComments(workitem_id):
    return getFile("ccm_workitem_comments.json")


@app.route('/ccm/oslc/workitems/catalog', methods=['GET'])
@requires_auth
def getCcmWorkitemsCatalog():
    return getFile("ccm_workitems_catalog.xml")


@app.route('/ccm/oslc/contexts/<context>/workitems/services.xml', methods=['GET'])
@requires_auth
def getCcmContextWorkitemsServices(context):
    if context == '_D6My4PJxEeiTkd5TZ1OBVQ':
        return getFile("ccm_context_workitems_services_2.xml")
    else:
        return getFile("ccm_context_workitems_services.xml")

# create a work item
@app.route('/ccm/oslc/contexts/<context>/workitems/com.ibm.team.workitem.workItemType.task', methods=['POST'])
@requires_auth
def getCcmCreateWorkitemTask(context):
    print request.data
    return getFile("ccm_create_workitem.json")

# update a work item
@app.route('/ccm/resource/itemName/com.ibm.team.workitem.WorkItem/<workitem_id>', methods=['PUT'])
@requires_auth
def getCcmUpdateWorkitemTask(workitem_id):
    print request.data
    return getFile("ccm_create_workitem.json")


if __name__ == '__main__':
    app.run(debug=True)
