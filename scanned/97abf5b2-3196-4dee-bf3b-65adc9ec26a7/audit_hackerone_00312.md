# [M] [public] Path traversal using symlink

## Summary
Severity: Medium (CVSS 4.2)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: henrychen
State: resolved
Disclosed: 2019-08-28T09:00:44.926Z
Source: https://hackerone.com/reports/593911

## Details
I would like to report Path traversal vulnerability in public module



# Module

**module name:** public
**version:** 0.1.4
**npm page:** `https://www.npmjs.com/package/public`

## Module Description

Run static file hosting server with specified public dir & port. Support a "direcotry index" like Apache httpd.



## Module Stats

105 downloads in the last week


# Vulnerability

## Vulnerability Description

Path traversal using symlink.



## Steps To Reproduce:

+ Install public 
```
npm install public -g
```
+ Run public server

```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/593911_
