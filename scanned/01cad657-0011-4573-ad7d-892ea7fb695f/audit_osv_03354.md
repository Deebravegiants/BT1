# [H] ALPINE-CVE-2025-59375

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-59375
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59375
Type: osv

## Affected
- Alpine:v3.19: `expat` — affected >=0 <2.7.2-r0
- Alpine:v3.20: `expat` — affected >=0 <2.7.2-r0
- Alpine:v3.21: `expat` — affected >=0 <2.7.2-r0
- Alpine:v3.22: `expat` — affected >=0 <2.7.2-r0
- Alpine:v3.23: `expat` — affected >=0 <2.7.2-r0
- Alpine:v3.24: `expat` — affected >=0 <2.7.2-r0

## Details
libexpat in Expat before 2.7.2 allows attackers to trigger large dynamic memory allocations via a small document that is submitted for parsing.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59375
