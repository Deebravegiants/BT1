# [M] Code Injection Vulnerability in morgan Package

## Summary
Severity: Medium (CVSS 6.8)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: cris_semmle
State: resolved
Disclosed: 2018-10-28T10:16:18.106Z
CVE: CVE-2019-5413
Source: https://hackerone.com/reports/390881

## Details
I would like to report a code injection vulnerability in morgan.
It allows an attacker to inject arbitrary JS commands in certain situations.

# Module

**module name:** morgan
**version:** 1.9.0
**npm page:** `https://www.npmjs.com/package/morgan`

## Module Description

HTTP request logger middleware for node.js

    Named after Dexter, a show you should not watch until completion.


## Module Stats

1,120,329 downloads in the last week

# Vulnerability

## Vulnerability Description

An attacker can use the format parameter to inject arbitrary commands

## Steps To Reproduce:

The basic attack vector looks like this: 
```js
var morgan = require('morgan');
var f = morgan('25 \\" + console.log(\'hello!\'); +  //:method :url :status :res[content-length] - :response-time ms');
f({}, {}, function () {
});
```
However, it is hard to believe that the package is used this way in any application. However, a more interesting attack vector is when combining this vulnerability with a prototype pollution one:

```js
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/390881_
