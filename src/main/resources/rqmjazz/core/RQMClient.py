# Copyright (c) 2019 XebiaLabs
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import sets
import sys
import unicodedata
import logging
import com.xhaus.jyson.JysonCodec as json
import xml.etree.ElementTree as ET

# from rqmjazz.core.HttpRequestPlus import HttpRequestPlus
from rqmjazz.core.HttpClient import HttpClient

logging.basicConfig(filename='log/plugin.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

# assortment of namespaces in the catalog xml
NAMESPACES = {
    'oslc_disc': 'http://open-services.net/xmlns/discovery/1.0/',
    'oslc': 'http://open-services.net/ns/core#',
    'dcterms': 'http://purl.org/dc/terms/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
}

# used to find ServiceProvider title which should equal the project area
TITLE_TAG = '{http://purl.org/dc/terms/}title'
# used to find the resource attribute of the ServiceProvider.details element
RESOURCE_KEY = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'

class RQMClient(object):
    logger = logging.getLogger('RtcClient')

    def __init__(self, http_connection, username=None, password=None, authheaders= {}, cookies = {}):
        self.http_request = HttpClient(http_connection, username, password, authheaders, cookies)

        # login to RQM server, get cookie for subsequent requests
        headers = {'Accept' : 'application/xml'}
        form_data = 'j_username=%s&j_password=%s' % (self.http_request.username, self.http_request.password)
        url = '/qm/service/com.ibm.rqm.common.service.rest.IOptionRestService/j_security_check'

        response = self.http_request.post(url, content=form_data, headers=headers)

        self.http_request.cookies = response.cookies


    @staticmethod
    def create_client(http_connection, username=None, password=None, authheaders= {}, cookies = {}):
        return RQMClient(http_connection, username, password, authheaders, cookies)


    def check_connection(self):
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        url = '/qm/rootservices'

        response = self.http_request.get(url, headers=headers)

        self.logger.debug('check_connection: status: %s' % str(response.status_code))

        return True

    # Unsure if this is useful
    # 1. Find out the URI for an existing iteration [HOW?] (there is no REST API to create an iteration). 

    # 2. Use the POST operation to create a test phase, and the request body (XML) should include 
    # <ns2:iteration href="https://clm.jkebanking.net:9443/qm/process/project-areas/_8aqdofQkEeex1tX1crJPcQ/timelines/_8kM0IPQkEeex1tX1crJPcQ/iterations/_q6R6pvQlEeex1tX1crJPcQ"/> 
    # <ns2:testplan href="https://clm.jkebanking.net:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/Money+that+Matters+%28Quality+Management%29/testplan/urn:com.ibm.rqm:testplan:10" /> 

    # 3. If successful, the response header "Location" contains the "slug" ID for the new test phase. 

    # 4. Use the POST operation to create a test suite execution record, and the request body (XML) should include 
    # <ns2:testplan href="https://clm.jkebanking.net:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/Money+that+Matters+%28Quality+Management%29/testplan/urn:com.ibm.rqm:testplan:10"/> 
    # <ns2:testsuite href="https://clm.jkebanking.net:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/Money+that+Matters+%28Quality+Management%29/testsuite/urn:com.ibm.rqm:testsuite:7"/> 
    # <ns2:testphase href="https://clm.jkebanking.net:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/Money+that+Matters+%28Quality+Management%29/testphase/slug__cY9gEvazEeex1tX1crJPcQ"/> 
    # Note: the test plan should be the same as the one at step 2, and the test suite should be associated in the same plan. 

    # 5. If successful, the response header "Location" contains the "slug" ID for the new test suite execution record. 

    # For more information, see https://jazz.net/wiki/bin/view/Main/RqmApi 

    # This along with the RQMExecutionTool code is useful
    # https://jazz.net/wiki/bin/view/Main/RQMExecutionTool
    def run_test_suite(self, project_area, tser_id):
        context_id = self._get_context_id(project_area)
        if context_id is None:
            raise Exception('Project area "%s" not found.' % project_area)

        self.logger.info('run_test_suite: context id: "%s"' % context_id)
        print('Running test plan in project "%s"' % context_id)

        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        url = '/service/com.ibm.rqm.execution.common.service.rest.ITestcaseExecutionRecordRestService/executeDTO'
        body = {
            'ewiId': tser_id,
            'projectAreaAlias': context_id
        }

        response = self.http_request.post(url, body, headers=headers)

        self.logger.info('run_test_suite: status: %s' % str(response.status_code))

        results_url = response.headers['Content-Location']
        return  results_url


    def get_test_results(self, result_url):
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}

        self.logger.info('get_test_results: result_url: "%s"' % result_url)
        print('Retrieving test results from "%s"' % result_url)

        response = self.http_request.get(result_url, headers=headers)

        self.logger.info('get_test_results: status: %s' % str(response.status_code))
        self.logger.debug('get_test_results: response: '+response.content)

        return response.content


    # private methods ---------------------------------

    # get the project context id give the project area
    def _get_context_id(self, project_area):
        headers = {'Accept' : 'application/xml'}
        url = '/qm/oslc_qm/catalog'

        response = self.http_request.get(url, headers=headers)

        root = ET.fromstring(response.content)

        # find project area
        for srvprov in root.findall('.//oslc:ServiceProvider', NAMESPACES):
            for child in srvprov:
                if child.tag == TITLE_TAG and child.text == project_area:
                    details = srvprov.find('./oslc:details', NAMESPACES)
                    attribs = details.attrib
                    if RESOURCE_KEY in attribs:
                        url = attribs[RESOURCE_KEY]
                        return url[url.rfind('/')+1:]

        return None


    def _print_info(self, obj):
        self.logger.debug('Type: %s' % type(obj))
        self.logger.debug('Vars: %s' % vars(obj))
        self.logger.debug('Dir:  %s' % dir(obj))
        self.logger.debug('obj ------\n')
        self.logger.debug(obj)

