# [M] ALPINE-CVE-2019-8905

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-8905
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8905
Type: osv

## Affected
- Alpine:v3.10: `file` — affected >=0 <5.36-r0
- Alpine:v3.11: `file` — affected >=0 <5.36-r0
- Alpine:v3.12: `file` — affected >=0 <5.36-r0
- Alpine:v3.13: `file` — affected >=0 <5.36-r0
- Alpine:v3.14: `file` — affected >=0 <5.36-r0
- Alpine:v3.15: `file` — affected >=0 <5.36-r0
- Alpine:v3.16: `file` — affected >=0 <5.36-r0
- Alpine:v3.17: `file` — affected >=0 <5.36-r0
- Alpine:v3.18: `file` — affected >=0 <5.36-r0
- Alpine:v3.19: `file` — affected >=0 <5.36-r0
- Alpine:v3.20: `file` — affected >=0 <5.36-r0
- Alpine:v3.21: `file` — affected >=0 <5.36-r0
- Alpine:v3.22: `file` — affected >=0 <5.36-r0
- Alpine:v3.23: `file` — affected >=0 <5.36-r0
- Alpine:v3.24: `file` — affected >=0 <5.36-r0
- Alpine:v3.7: `file` — affected >=0 <5.32-r1
- Alpine:v3.8: `file` — affected >=0 <5.32-r1
- Alpine:v3.9: `file` — affected >=0 <5.36-r0

## Details
do_core_note in readelf.c in libmagic.a in file 5.35 has a stack-based buffer over-read, related to file_printable, a different vulnerability than CVE-2018-10360.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8905
