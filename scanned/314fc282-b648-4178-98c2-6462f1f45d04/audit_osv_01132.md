# [M] ALPINE-CVE-2018-20482

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20482
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20482
Type: osv

## Affected
- Alpine:v3.10: `tar` — affected >=0 <1.31-r0
- Alpine:v3.11: `tar` — affected >=0 <1.31-r0
- Alpine:v3.12: `tar` — affected >=0 <1.31-r0
- Alpine:v3.13: `tar` — affected >=0 <1.31-r0
- Alpine:v3.14: `tar` — affected >=0 <1.31-r0
- Alpine:v3.15: `tar` — affected >=0 <1.31-r0
- Alpine:v3.16: `tar` — affected >=0 <1.31-r0
- Alpine:v3.17: `tar` — affected >=0 <1.31-r0
- Alpine:v3.18: `tar` — affected >=0 <1.31-r0
- Alpine:v3.19: `tar` — affected >=0 <1.31-r0
- Alpine:v3.20: `tar` — affected >=0 <1.31-r0
- Alpine:v3.21: `tar` — affected >=0 <1.31-r0
- Alpine:v3.22: `tar` — affected >=0 <1.31-r0
- Alpine:v3.23: `tar` — affected >=0 <1.31-r0
- Alpine:v3.24: `tar` — affected >=0 <1.31-r0
- Alpine:v3.6: `tar` — affected >=0 <1.31-r0
- Alpine:v3.7: `tar` — affected >=0 <1.31-r0
- Alpine:v3.8: `tar` — affected >=0 <1.31-r0
- Alpine:v3.9: `tar` — affected >=0 <1.31-r0

## Details
GNU Tar through 1.30, when --sparse is used, mishandles file shrinkage during read access, which allows local users to cause a denial of service (infinite read loop in sparse_dump_region in sparse.c) by modifying a file that is supposed to be archived by a different user's process (e.g., a system backup running as root).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20482
