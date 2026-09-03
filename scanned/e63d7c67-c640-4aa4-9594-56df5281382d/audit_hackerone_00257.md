# [H] [jsreport] Remote Code Execution

## Summary
Severity: High (CVSS 8.0)
Program: Node.js third-party modules
Weakness: Remote File Inclusion
Reporter: ermilov
State: resolved
Disclosed: 2020-02-07T15:24:08.771Z
CVE: CVE-2020-8128
Source: https://hackerone.com/reports/660565

## Details
I would like to report Remote Code Execution in `jsreport`
It allows running js files remotely on a vulnerable server.

# Module

**module name:** jsreport
**version:** 2.5.0
**npm page:** `https://www.npmjs.com/package/jsreport`

## Module Description

jsreport is a reporting server which lets developers define reports using javascript templating engines (like jsrender or handlebars). It supports various report output formats like html, pdf, excel and others. It also includes advanced reporting features like user management, REST API, scheduling, designer or sending emails.

## Module Stats

52 downloads in the last day
2056 downloads in the last week
6428 downloads in the last month

# Vulnerability

## Vulnerability Description

`jsreport` consists of a variety of packages which combines in one working application. `Script-manager` is one of them, it is utilized for running user's scripts in a sandbox and has an `unintended require` vulnerability (I have a separate report describing this vulnerability) which allows an attacker to load code that was not intended to execute. Another module is `Puppeteer` which is headless Chrome Node API. The application uses it for turning user's HTML into pdf files and unfortunately, the way it is applied allows fetching URLs and sending requests defined in an HTML file by a user which is known as SSRF (Server Side Request Forgery). Chaining these two vulnerabilities (Unintended require + SSRF) leads to remote code execution possibility.

**SSRF:**
SSRF itself is quite simple, generating a pdf report from an HTML template like this one:

    <html>
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    </head>
    <body>
    		<!-- will send GET request to example.com -->
        <img src="http://example.com/" />
    		<!-- will send POST request to example.com -->
    		<form id="pwn-form" method="POST" action="http://example.com/action">
            <input type="hidden" name='SomeField' value='Some Value' />

_Trimmed to 38 lines — full report: https://hackerone.com/reports/660565_
