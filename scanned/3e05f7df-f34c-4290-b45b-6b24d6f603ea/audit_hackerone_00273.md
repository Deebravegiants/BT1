# [M] Path traversal in https://www.npmjs.com/package/http_server via symlink

## Summary
Severity: Medium (CVSS 5.5)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: vineetpandey
State: resolved
Disclosed: 2019-12-04T19:56:48.103Z
CVE: CVE-2019-15600
Source: https://hackerone.com/reports/692262

## Details
I would like to report Path traversal in http_server
It allows an attacker to read arbitrary system files.

# Module

**module name:** http_server
**version:** 1.0.12
**npm page:** `https://www.npmjs.com/package/http_server`

## Module Description

> Copy description from npm page

## Module Stats

Weekly downloads: 35

# Vulnerability

## Vulnerability Description

With a symbolically linked file in the working directory, it is possible to read arbitrary files outside of the web root directory.

## Steps To Reproduce:

1. Install the http_server: npm install http_server -g

2. Create a symlink file within the directory
ln -s /etc/shadow test_shadow

3. Request the file within browser
http://localhost:8888/test_shadow

## Patch

Reject the symbolically linked path files.

## Supporting Material/References:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/692262_
