# [H] @adonisjs/bodyparser has an incomplete fix for CVE-2026-25754

## Summary
Severity: High
Advisory: GHSA-qcm7-3vpr-hj5h
CVE: CVE-2026-48795
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-qcm7-3vpr-hj5h
Type: github-advisory

## Affected
- npm: `@adonisjs/bodyparser` — affected >=10.1.3 <10.1.5
- npm: `@adonisjs/bodyparser` — affected >=11.0.0-next.9 <11.0.3

## Details
### Summary

The fix for [GHSA-f5x2-vj4h-vg4c](https://github.com/adonisjs/core/security/advisories/GHSA-f5x2-vj4h-vg4c) / CVE-2026-25754 introduced in commit [`40e1c71`](https://github.com/adonisjs/bodyparser/commit/40e1c71f958cffb74f6b91bed6630dca979062ed) is incomplete and can be bypassed through nested prototype pollution payloads.

The original patch replaced the internal `FormFields` storage object with `Object.create(null)`, preventing direct payloads such as `__proto__.polluted`. However, payloads containing a non-dangerous segment before `__proto__` or `constructor.prototype`, such as `user.__proto__.polluted`, still lead to `Object.prototype` pollution.

This issue is exploitable remotely through a single unauthenticated `multipart/form-data` request using the default configuration.

### Affected versions

- `>= 10.1.3 < 10.1.5`
- `>= 11.0.0-next.9 < 11.0.3`

### Details

The regression tests added by the original fix only covered direct payloads such as:

- `__proto__.polluted`
- `constructor.prototype.polluted`

These payloads are blocked because the root object no longer inherits from `Object.prototype`.

However, lodash `_.set()` (via `@poppinss/utils`) still creates intermediate objects using plain `{}` values. Once a normal segment is encountered, subsequent `__proto__` or `constructor.prototype` segments regain access to `Object.prototype`.

### Impact

An unauthenticated attacker can remotely pollute `Object.prototype` on any route accepting multipart/form-data requests behind `BodyParserMiddleware`.

Because the pollution is process-wide, the impact may include authorization bypasses, unexpected behavior in downstream libraries, or prototype pollution gadget chains leading to remote code execution.

### Patches

Fixes targeting v6 and v7 have been published below.

Users should upgrade to a version that includes the following fix:

- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.5
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.3

### References

- [CWE-1321](https://cwe.mitre.org/data/definitions/1321.html)
- Prior advisory this bypasses: [GHSA-f5x2-vj4h-vg4c](https://github.com/adonisjs/core/security/advisories/GHSA-f5x2-vj4h-vg4c) / CVE-2026-25754

## References
- https://github.com/adonisjs/core/security/advisories/GHSA-f5x2-vj4h-vg4c
- https://github.com/adonisjs/core/security/advisories/GHSA-qcm7-3vpr-hj5h
- https://github.com/adonisjs/bodyparser/commit/40e1c71f958cffb74f6b91bed6630dca979062ed
- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.5
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.3
- https://github.com/adonisjs/core
