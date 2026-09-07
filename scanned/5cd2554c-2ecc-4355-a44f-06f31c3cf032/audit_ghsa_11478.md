# [M] Handlebars.js has Prototype Pollution Leading to XSS through Partial Template Injection

## Summary
Severity: Medium
Advisory: GHSA-2qvq-rjwj-gvw9
CVE: CVE-2026-33916
CWE: CWE-1321, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-2qvq-rjwj-gvw9
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.7.9

## Details
## Summary

`resolvePartial()` in the Handlebars runtime resolves partial names via a plain property lookup on `options.partials` without guarding against prototype-chain traversal. When `Object.prototype` has been polluted with a string value whose key matches a partial reference in a template, the polluted string is used as the partial body and rendered **without HTML escaping**, resulting in reflected or stored XSS.

## Description

The root cause is in `lib/handlebars/runtime.js` inside `resolvePartial()` and `invokePartial()`:

```javascript
// Vulnerable: plain bracket access traverses Object.prototype
partial = options.partials[options.name];
```

`hasOwnProperty` is never checked, so if `Object.prototype` has been seeded with a key whose name matches a partial reference in the template (e.g. `widget`), the lookup succeeds and the polluted string is returned. The runtime emits a prototype-access warning, but the partial is still resolved and its content is inserted into the rendered output unescaped. This contradicts the documented security model and is distinct from CVE-2021-23369 and CVE-2021-23383, which addressed data property access rather than partial template resolution.

**Prerequisites for exploitation:**
1. The target application must be vulnerable to prototype pollution (e.g. via `qs`, `minimist`, or
   any querystring/JSON merge sink).
2. The attacker must know or guess the name of a partial reference used in a template.

## Proof of Concept

```javascript
const Handlebars = require('handlebars');

// Step 1: Prototype pollution (via qs, minimist, or another vector)
Object.prototype.widget = '<img src=x onerror="alert(document.domain)">';

// Step 2: Normal template that references a partial
const template = Handlebars.compile('<div>Welcome! {{> widget}}</div>');

// Step 3: Render — XSS payload injected unescaped
const output = template({});
// Output: <div>Welcome! <img src=x onerror="alert(document.domain)"></div>
```

> The runtime prints a prototype access warning claiming "access has been denied," but the partial still resolves and returns the polluted value.

## Workarounds

- Apply `Object.freeze(Object.prototype)` early in application startup to prevent prototype  pollution. Note: this may break other libraries.
- Use the Handlebars runtime-only build (`handlebars/runtime`), which does not compile templates  and reduces the attack surface.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-2qvq-rjwj-gvw9
- https://nvd.nist.gov/vuln/detail/CVE-2021-23369
- https://nvd.nist.gov/vuln/detail/CVE-2021-23383
- https://nvd.nist.gov/vuln/detail/CVE-2026-33916
- https://github.com/handlebars-lang/handlebars.js/commit/68d8df5a88e0a26fe9e6084c5c6aaebe67b07da2
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
