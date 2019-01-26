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

from rqmjazz.core.HttpRequestPlus import HttpRequestPlus

logging.basicConfig(filename='log/plugin.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

HTTP_SUCCESS = sets.Set([200, 201, 204])

NAMESPACES = {
    'oslc_disc': 'http://open-services.net/xmlns/discovery/1.0/',
    'dcterms': 'http://purl.org/dc/terms/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
}

class RQMClient(object):
    httpRequest = None
    logger = logging.getLogger('RtcClient')

    def __init__(self, httpConnection, username=None, password=None):
        self.logger.info('__init__ : %s' % repr(httpConnection))
        self.httpRequest = HttpRequestPlus(httpConnection, username, password)

    @staticmethod
    def createClient(httpConnection, username=None, password=None):
        return RQMClient(httpConnection, username, password)


    def check_connection(self):
        contentType = "application/json"
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        url = '/qm/rootservices'

        response = self.httpRequest.get(url, contentType=contentType, headers=headers)
        if response.getStatus() not in HTTP_SUCCESS:
            self._error('Unable to check connection', response)

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
            self._error('Project area "%s" not found.' % project_area)

        self.logger.debug('run_test_suite: context id: "%s"' % context_id)
        print 'Running test plan in project "%s"' % context_id

        contentType = "application/json"
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        url = '/service/com.ibm.rqm.execution.common.service.rest.ITestcaseExecutionRecordRestService/executeDTO'
        body = {
            'ewiId': tser_id,
            'projectAreaAlias': context_id
        }

        response = self.httpRequest.post(url, body, contentType=contentType, headers=headers)
        if response.getStatus() not in HTTP_SUCCESS:
            self._error('Unable to run test suite', response)

        self.logger.debug('run_test_suite: response: '+response.response)

        return response.header['Content-Location'] # result_url


    def get_test_results(self, result_url):
        
        contentType = "application/json"
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}

        response = self.httpRequest.get(result_url, contentType=contentType, headers=headers)
        if response.getStatus() not in HTTP_SUCCESS:
            self._error('Unable to get test results', response)

        self.logger.debug('run_test_suite: response: '+response.response)

        return response.response


    # private methods ---------------------------------

    # get the project context id give the project area
    def _get_context_id(self, project_area):
        contentType = "application/json"
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        url = '/qm/oslc_qm/catalog'

        response = self.httpRequest.get(url, contentType=contentType, headers=headers)
        if response.getStatus() not in HTTP_SUCCESS:
            self._error('Unable to create work item, catalog request failed.', response)

        ascii_xml = self._strip_unicode(response.response)
        root = ET.fromstring(ascii_xml)

        # find project area
        for srvprov in root.iterfind('.//oslc_disc:ServiceProvider', NAMESPACES):
            for child in srvprov:
                if child.tag == '{http://purl.org/dc/terms/}title' and child.text == project_area:
                    url = srvprov.find('./oslc_disc:details', NAMESPACES).attrib.values()[0]
                    return url[url.rfind('/')+1:]
    
        return None

