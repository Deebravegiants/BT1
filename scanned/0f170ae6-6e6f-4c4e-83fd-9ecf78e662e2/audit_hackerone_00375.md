# [H] `superstatic` is vulnerable to path traversal on Windows

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: chalker
State: resolved
Disclosed: 2018-04-29T16:10:30.241Z
Source: https://hackerone.com/reports/319951

## Details
I would like to report path traversal vulnerability in `superstatic`
It allows to read arbitrary out-of-dir files when running on the Windows platform

# Module

**module name:** `superstatic`
**version:** 5.0.1
**npm page:** `https://www.npmjs.com/package/superstatic`

## Module Description

> Superstatic is an enhanced static web server that was built to power. It has fantastic support for HTML5 pushState applications, clean URLs, caching, and many other goodies.

## Module Stats

2 196 downloads in the last day
33 588 downloads in the last week
139 118 downloads in the last month

~1 669 416 estimated downloads per year

# Vulnerability

## Vulnerability Description

`superstatic` verifies that current dir is not evaded by checking the presense of `../` in the decoded path, but on Windows, `..\` works.
Code: https://github.com/firebase/superstatic/blob/v5.0.1/lib/providers/fs.js#L71

## Steps To Reproduce:

Install and run superstatic (`npx superstatic` in any dir). It could be also used as a Node.js lib.

Go to `http://localhost:3474/..%5c..%5c..%5c/Windows/notepad.exe` (adjust the path accordingly, that's for `C:\Users\User\tmp`).

*Note: don't use Edge for that, it decodes the path itself. Use e.g. Chromium.*

## Supporting Material/References:


_Trimmed to 38 lines — full report: https://hackerone.com/reports/319951_
