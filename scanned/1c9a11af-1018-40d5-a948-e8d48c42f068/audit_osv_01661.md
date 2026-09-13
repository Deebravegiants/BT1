# [H] ALPINE-CVE-2019-8904

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-8904
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8904
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
- Alpine:v3.9: `file` — affected >=0 <5.36-r0

## Details
do_bid_note in readelf.c in libmagic.a in file 5.35 has a stack-based buffer over-read, related to file_printf and file_vprintf.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8904
