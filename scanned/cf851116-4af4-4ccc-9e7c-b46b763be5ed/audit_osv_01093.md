# [M] ALPINE-CVE-2018-19886

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19886
Ecosystem: Alpine:v3.10, Alpine:v3.11
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19886
Type: osv

## Affected
- Alpine:v3.10: `faac` — affected >=0 <1.30-r0
- Alpine:v3.11: `faac` — affected >=0 <1.30-r0

## Details
An invalid memory address dereference was discovered in the huffcode function (libfaac/huff2.c) in Freeware Advanced Audio Coder (FAAC) 1.29.9.2. The vulnerability causes a segmentation fault and application crash, which leads to denial of service in the book 8 case.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19886
