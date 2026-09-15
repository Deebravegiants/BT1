# [M] ALPINE-CVE-2019-1010305

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1010305
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1010305
Type: osv

## Affected
- Alpine:v3.10: `libmspack` — affected >=0 <0.8_alpha-r1
- Alpine:v3.11: `libmspack` — affected >=0 <0.10.1_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.8_alpha-r1
- Alpine:v3.9: `libmspack` — affected >=0 <0.8_alpha-r1

## Details
libmspack 0.9.1alpha is affected by: Buffer Overflow. The impact is: Information Disclosure. The component is: function chmd_read_headers() in libmspack(file libmspack/mspack/chmd.c). The attack vector is: the victim must open a specially crafted chm file. The fixed version is: after commit 2f084136cfe0d05e5bf5703f3e83c6d955234b4d.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1010305
