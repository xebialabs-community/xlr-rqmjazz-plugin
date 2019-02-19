# XL Release Plugin for IBM Rational Quality Manager (RQM) #

[![Build Status][xlr-rqm-plugin-travis-image]][xlr-rqm-plugin-travis-url]
[![License: MIT][xlr-rqm-plugin-license-image]][xlr-rqm-plugin-license-url]
![Github All Releases][xlr-rqm-plugin-downloads-image]

[xlr-rqm-plugin-travis-image]: https://travis-ci.org/xebialabs-community/xlr-rqm-plugin.svg?branch=master
[xlr-rqm-plugin-travis-url]: https://travis-ci.org/xebialabs-community/xlr-rqm-plugin
[xlr-rqm-plugin-license-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[xlr-rqm-plugin-license-url]: https://opensource.org/licenses/MIT
[xlr-rqm-plugin-downloads-image]: https://img.shields.io/github/downloads/xebialabs-community/xlr-rqm-plugin/total.svg

# Overview #

**NOTE: This plugin is not fully tested and likely does not work. It is intended as a starting point for an upcoming customer implementation engagement.**

This plugin provides the ability to manipulate work items in IBM rqm.

See the **XL Release Reference Manual** for background information on XL Release and plugin concepts.

* **Requirements**
  * **XL Release** 7.5.0+
  * **IBM RQM** 6.0.3+

# Installation #

* Copy the latest JAR file from the [releases page](https://github.com/xebialabs-community/xlr-rqm-plugin/releases) into the `XL_RELEASE_SERVER/plugins/__local__` directory.
* Restart the XL Release server.

# Usage #

## Configure Server ##

Begin by configuring one or more rqm servers.  Navigate to **Settings -> Shared configuration** and add a rqm: Server.

![rqmServerConfig](images/rqm-server-config.png)



### Title ###

Enter a descriptive name for this server.

### URL ###

Enter the full URL to the server.  Include protocol (http or https) and port number if applicable.

### Username ###

The current versions of rqm (12.0 and below) do not use authentication so no username or password is needed.  When future versions of rqm require authentication, enter the username here.

### Password ###

When future versions of rqm require authentication, enter the password here.

### Domain ###

The NTLM domain for authentication if applicable.

### Proxy ###

Optional proxy information if you access the rqm server through a proxy.

---

## Run Test Suite ##

In your SDLC templates, you can add a task of type **rqm -> Run Test Suite** as shown below.  

![rqm-run-suite-1](images/rqm-run-suite-1.png)

### Server ###

The RQM Server that will run your tests.

---

### Example Output ###

Once the task is complete you will see output like these shown below...

![rqm-run-suite-2](images/rqm-run-suite-2.png)

## Retrieve Test Results ##

In your SDLC templates, you can add a task of type **rqm -> Retrieve Test Results** as shown below.  This will retrieve test results including result status as output variables.

![rqm-get-results-1](images/rqm-get-results-1.png)

### Server ###

The RQM Server that has your tests results.

---

### Example Output ###

Once the task is complete you will see output like these shown below...

![rqm-get-results-2](images/rqm-get-results-2.png)



# Developers #

Build and package the plugins with...

```bash
./gradlew assemble
```

Run unit tests with...

```bash
./gradlew pyTest
```