# [H] ALPINE-CVE-2021-40633

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-40633
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-06-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40633
Type: osv

## Affected
- Alpine:v3.17: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.18: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.19: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.20: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.21: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.22: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.23: `giflib` — affected >=0 <5.2.2-r0
- Alpine:v3.24: `giflib` — affected >=0 <5.2.2-r0

## Details
A memory leak (out-of-memory) in gif2rgb in util/gif2rgb.c in giflib 5.1.4 allows remote attackers trigger an out of memory exception or denial of service via a gif format file.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40633
