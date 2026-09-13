# [M] ALPINE-CVE-2026-14672

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-14672
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14672
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
Observable response discrepancy in PostgreSQL SCRAM authentication allows an unauthenticated user to test the existence of a user via observing the SCRAM iteration count.  This requires the probed user to have a non-default scram_iterations count, because the authentication challenge for a nonexistent user reports the default scram_iterations.  Within major versions 16-18, minor versions before PostgreSQL 18.6, 17.11, and 16.15 are affected.  Versions before PostgreSQL 16 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14672
