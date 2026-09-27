# [M] ALPINE-CVE-2026-14666

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-14666
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14666
Type: osv

## Affected
- Alpine:v3.21: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
Incomplete tracking in PostgreSQL of changes to role membership, role attributes, and database ownership allows a query to continue using cached row-level security policies after those changes require a different policy, via plan reuse.  Stale policies continue until some other event invalidates the cache or connection termination ends the session.  This permits a user to complete reads and modifications that were recently permitted but now forbidden.  An attacker must tailor an attack to a particular application's pattern of privilege removal and role-specific row security policies.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14666
