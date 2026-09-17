# [H] ALPINE-CVE-2021-45960

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-45960
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-45960
Type: osv

## Affected
- Alpine:v3.12: `expat` — affected >=0 <2.2.10-r0
- Alpine:v3.13: `expat` — affected >=0 <2.2.10-r2
- Alpine:v3.14: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.15: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.16: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.17: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.18: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.19: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.20: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.21: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.22: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.23: `expat` — affected >=0 <2.4.3-r0
- Alpine:v3.24: `expat` — affected >=0 <2.4.3-r0

## Details
In Expat (aka libexpat) before 2.4.3, a left shift by 29 (or more) places in the storeAtts function in xmlparse.c can lead to realloc misbehavior (e.g., allocating too few bytes, or only freeing memory).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-45960
