# [M] ALPINE-CVE-2026-21717

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-21717
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21717
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A flaw in V8's string hashing mechanism causes integer-like strings to be hashed to their numeric value, making hash collisions trivially predictable. By crafting a request that causes many such collisions in V8's internal string table, an attacker can significantly degrade performance of the Node.js process.

The most common trigger is any endpoint that calls `JSON.parse()` on attacker-controlled input, as JSON parsing automatically internalizes short strings into the affected hash table.

This vulnerability affects **20.x, 22.x, 24.x, and 25.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21717
