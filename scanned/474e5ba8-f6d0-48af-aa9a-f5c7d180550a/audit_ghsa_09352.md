# [H] @theecryptochad/merge-guard has Prototype Pollution in its deepMerge() function

## Summary
Severity: High
Advisory: GHSA-mhwj-73qx-jqxm
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-mhwj-73qx-jqxm
Type: github-advisory

## Affected
- npm: `@theecryptochad/merge-guard` — affected >=0 <1.0.1

## Details
## Summary

`@theecryptochad/merge-guard` versions prior to 1.0.1 are vulnerable to Prototype Pollution via the `deepMerge()` function. An attacker who controls the source object can inject `__proto__` keys that mutate `Object.prototype`, affecting all objects in the Node.js runtime.

## Details

The `deepMerge()` function recursively merges two objects without sanitizing reserved property keys (`__proto__`, `constructor`, `prototype`). When a source object contains a `__proto__` key, its value is assigned to `target.__proto__`, which JavaScript engines interpret as a write to `Object.prototype`.

## Proof of Concept

```js
const { deepMerge } = require('@theecryptochad/merge-guard');
const payload = JSON.parse('{"__proto__":{"isAdmin":true}}');
deepMerge({}, payload);
console.log({}.isAdmin); // true — Object.prototype is polluted
```

## Impact

Any application using `deepMerge()` with untrusted input (e.g. user-supplied JSON from HTTP requests, WebSocket messages, or config files) is vulnerable. An attacker can inject arbitrary properties onto `Object.prototype`, enabling privilege escalation, application logic bypass, and property injection.

## Remediation

Upgrade to `@theecryptochad/merge-guard >= 1.0.1`, which adds an explicit blocklist:

```js
const BLOCKED = new Set(['__proto__', 'constructor', 'prototype']);
if (BLOCKED.has(key)) continue;
```

## References
- [CWE-1321: Improper Neutralization of Special Elements in Object Keys](https://cwe.mitre.org/data/definitions/1321.html)
- [OWASP: Prototype Pollution](https://owasp.org/www-community/attacks/Prototype_Pollution)
- [Fix commit](https://github.com/TheeCryptoChad/merge-guard/releases/tag/v1.0.1)

## References
- https://github.com/TheeCryptoChad/merge-guard/security/advisories/GHSA-mhwj-73qx-jqxm
- https://github.com/TheeCryptoChad/merge-guard/commit/25e4b4f2618578a656ef3cb4946a1b475f736736
- https://github.com/TheeCryptoChad/merge-guard
