# [M] ALPINE-CVE-2026-32778

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-32778
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32778
Type: osv

## Affected
- Alpine:v3.20: `expat` — affected >=0 <2.7.5-r0
- Alpine:v3.21: `expat` — affected >=0 <2.7.5-r0
- Alpine:v3.22: `expat` — affected >=0 <2.7.5-r0
- Alpine:v3.23: `expat` — affected >=0 <2.7.5-r0
- Alpine:v3.24: `expat` — affected >=0 <2.7.5-r0

## Details
libexpat before 2.7.5 allows a NULL pointer dereference in the function setContext on retry after an earlier ouf-of-memory condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32778
