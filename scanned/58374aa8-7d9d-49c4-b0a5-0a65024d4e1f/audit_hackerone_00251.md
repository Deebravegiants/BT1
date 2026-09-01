# [H] Server Side Request Forgery in Uppy npm module

## Summary
Severity: High (CVSS 8.2)
Program: Node.js third-party modules
Weakness: Server-Side Request Forgery (SSRF)
Reporter: 3sl4m-s4l3m
State: resolved
Disclosed: 2020-03-02T07:38:09.438Z
CVE: CVE-2020-8135
Source: https://hackerone.com/reports/786956

## Details
Hi Team,

While we were testing our security engine at Shieldfy (https://shieldfy.io), We found a server side request forgery (SSRF) vulnerability in Uppy npm package.
It allows hacker to easily extract inside information from the server or take control of internal services.

# Module

**module name:**  Uppy
**version:** Latest: 1.8.0
**npm page:** `https://www.npmjs.com/package/uppy`

## Module Description

Uppy is a sleek, modular JavaScript file uploader that integrates seamlessly with any application. It’s fast, easy to use and lets you worry about more important problems than building a file uploader.

## Module Stats

[1] weekly downloads : 23,153

# Vulnerability
Server Side Request Forgery ( SSRF )

## Vulnerability Description

in the source code of the module
file: [packages/@uppy/companion/src/server/controllers/url.js line: 11](https://github.com/transloadit/uppy/blob/746bbcbbc5dc64203390322b28fb380ec67bd94f/packages/%40uppy/companion/src/server/controllers/url.js#L11)


You will find the express is routing the `/get` endpoint to the [function `get` declared in line 43](https://github.com/transloadit/uppy/blob/746bbcbbc5dc64203390322b28fb380ec67bd94f/packages/%40uppy/companion/src/server/controllers/url.js#L43)

Then it calls [`downloadURL` in line`61](https://github.com/transloadit/uppy/blob/746bbcbbc5dc64203390322b28fb380ec67bd94f/packages/%40uppy/companion/src/server/controllers/url.js#L61) and pass `req.body.url` to it as argument


in the function [`downloadURL`  declared in line 80](https://github.com/transloadit/uppy/blob/746bbcbbc5dc64203390322b28fb380ec67bd94f/packages/%40uppy/companion/src/server/controllers/url.js#L80)


It calls the url directly without any kind of sanitization or validation, opens the door to send malicious ssrf attack, allowing the hacker to extract information from any internal resource, or take control of any internal service.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/786956_
