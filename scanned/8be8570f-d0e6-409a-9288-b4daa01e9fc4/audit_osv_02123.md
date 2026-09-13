# [H] ALPINE-CVE-2021-25290

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-25290
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25290
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.2-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.2-r0

## Details
An issue was discovered in Pillow before 8.1.1. In TiffDecode.c, there is a negative-offset memcpy with an invalid size.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25290
