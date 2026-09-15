# [H] @nevware21/ts-utils: Prototype Pollution in objDeepCopy/objCopyProps via for...in without hasOwnProperty

## Summary
Severity: High
Advisory: GHSA-x7j8-49r8-mr43
CVE: CVE-2026-46681
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-x7j8-49r8-mr43
Type: github-advisory

## Affected
- npm: `@nevware21/ts-utils` — affected >=0 <0.14.0

## Details
## Summary

The _copyProps function in lib/src/object/copy.ts uses for...in to iterate over source object properties without an Object.hasOwnProperty check, and does not filter dangerous keys (__proto__, constructor, prototype). This allows an attacker to pollute the prototype chain of all objects in the application.

## Details

In _copyProps() (copy.ts lines 186-191), the code iterates all enumerable properties including inherited ones and dangerous keys like __proto__. Any object with a __proto__ key (e.g., from untrusted JSON input) will overwrite the target's prototype.

## PoC
```
const malicious = JSON.parse('{"__proto__": {"polluted": true}}');
objDeepCopy(malicious);
console.log({}.polluted); // true
```
## Suggested Fix

Add objHasOwnProperty check and filter __proto__, constructor, prototype keys.

## References
- https://github.com/nevware21/ts-utils/security/advisories/GHSA-x7j8-49r8-mr43
- https://github.com/nevware21/ts-utils
