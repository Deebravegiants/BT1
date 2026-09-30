# [M] Hono vulnerable to Prototype Pollution possible through __proto__ key allowed in parseBody({ dot: true })

## Summary
Severity: Medium
Advisory: GHSA-v8w9-8mx6-g223
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-v8w9-8mx6-g223
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.7

## Details
## Summary

When using `parseBody({ dot: true })` in HonoRequest, specially crafted form field names such as `__proto__.x` could create objects containing a `__proto__` property.

If the parsed result is later merged into regular JavaScript objects using unsafe merge patterns, this may lead to prototype pollution in the target object.

## Details

The `parseBody({ dot: true })` feature supports dot notation to construct nested objects from form field names.

In previous versions, the `__proto__` path segment was not filtered. As a result, specially crafted keys such as `__proto__.x` could produce objects containing `__proto__` properties.

While this behavior does not directly modify `Object.prototype` within Hono itself, it may become exploitable if the parsed result is later merged into regular JavaScript objects using unsafe merge patterns.

## Impact

Applications that merge parsed form data into regular objects using unsafe patterns (for example recursive deep merge utilities) may become vulnerable to prototype pollution.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-v8w9-8mx6-g223
- https://github.com/honojs/hono/commit/ef902257e0beacbb83d2a9549b3b83e03514a6fe
- https://github.com/honojs/hono
