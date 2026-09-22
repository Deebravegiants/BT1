# [H] ALPINE-CVE-2026-41254

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41254
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41254
Type: osv

## Affected
- Alpine:v3.20: `lcms2` — affected >=0 <2.19-r0
- Alpine:v3.21: `lcms2` — affected >=0 <2.19-r0
- Alpine:v3.22: `lcms2` — affected >=0 <2.19-r0
- Alpine:v3.23: `lcms2` — affected >=0 <2.19-r0
- Alpine:v3.24: `lcms2` — affected >=0 <2.19-r0

## Details
Little CMS (lcms2) through 2.18 has an integer overflow in CubeSize in cmslut.c because the overflow check is performed after the multiplication.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41254
