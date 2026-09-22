# [H] ALPINE-CVE-2026-6638

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6638
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6638
Type: osv

## Affected
- Alpine:v3.20: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
SQL injection in PostgreSQL logical replication ALTER SUBSCRIPTION ... REFRESH PUBLICATION allows a subscriber table creator to execute arbitrary SQL with the subscription's publication-side credentials.  The attack takes effect at the next REFRESH PUBLICATION.  Within major versions 16, 17, and 18, minor versions before PostgreSQL 18.4, 17.10, and 16.14 are affected.  Versions before PostgreSQL 16 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6638
