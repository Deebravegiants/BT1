# [M] Command injection in 'pdf-image'

## Summary
Severity: Medium (CVSS 6.1)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: defmax
State: resolved
Disclosed: 2018-05-29T20:43:43.830Z
CVE: CVE-2018-3757
Source: https://hackerone.com/reports/340208

## Details
I would like to report command injection in pdf-image
It allows executing commands on the server 

# Module

**module name:** pdf-image
**version:** 1.0.5
**npm page:** `https://www.npmjs.com/package/pdf-image`

## Module Description

> Provides an interface to convert PDF's pages to png files in Node.js by using ImageMagick.


## Module Stats

[2013] downloads in the last week

# Vulnerability

## Vulnerability Description

> Description about how the vulnerability was found and how it can be exploited, how it harms package users (data modification/lost, system access, other.

## Steps To Reproduce:

> The constructGetInfoCommand would be initializing the command that is to the passed to 'exec' of getInfo(). The user input is not getting validated in #L26 of constructGetInfoCommand and it leads to command injection in #L43.

https://github.com/mooz/node-pdf-image/blob/master/index.js#L26
https://github.com/mooz/node-pdf-image/blob/master/index.js#L43## Patch

## Supporting Material/References:

> State all technical information about the stack where the vulnerability was found

- Kali linux 
- Nodejs v8.10.0
- Npm v5.8.0

_Trimmed to 38 lines — full report: https://hackerone.com/reports/340208_
