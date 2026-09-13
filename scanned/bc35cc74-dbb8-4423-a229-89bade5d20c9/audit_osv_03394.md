# [H] ALPINE-CVE-2025-6965

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-6965
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-6965
Type: osv

## Affected
- Alpine:v3.18: `sqlite` — affected >=0 <3.41.2-r4
- Alpine:v3.19: `sqlite` — affected >=0 <3.44.2-r2
- Alpine:v3.20: `sqlite` — affected >=0 <3.45.3-r3
- Alpine:v3.21: `sqlite` — affected >=0 <3.48.0-r3
- Alpine:v3.22: `sqlite` — affected >=0 <3.49.2-r1

## Details
There exists a vulnerability in SQLite versions before 3.50.2 where the number of aggregate terms could exceed the number of columns available. This could lead to a memory corruption issue. We recommend upgrading to version 3.50.2 or above.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-6965
