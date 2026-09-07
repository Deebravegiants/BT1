# [M] List any file in the folder by using path traversal

## Summary
Severity: Medium (CVSS 6.8)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: vulzzz
State: resolved
Disclosed: 2018-11-23T08:03:07.307Z
CVE: CVE-2018-16478
Source: https://hackerone.com/reports/403703

## Details
I would like to report Path Traversal in simplehttpserver. It allows to list any file in another folder of web root.

# Module

**module name:** simplehttpserver
**version:** v0.2.1
**npm page:** `https://www.npmjs.com/package/simplehttpserver`

## Module Description

 'simpehttpserver' is an simple imitation of python's SimpleHTTPServer and is intended for testing, development and debugging purposes

## Module Stats

 [319] downloads in the last week

# Vulnerability

## Vulnerability Description

 simpehttpserver is simply get the path name of url and add it to the web root.If there is a symlink file in the directory. You can access files outside the web root directory.

## Steps To Reproduce:
 create symlink file 
$ ln -s ../../ symdir

 install simplehttpserver
$ npm install simplehttpserver -g

start program
$ simplehttpserver ./

{F340863}

## Patch

Disable symlink file access in webserver.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/403703_
