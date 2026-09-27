# [H] ALPINE-CVE-2022-1304

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1304
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1304
Type: osv

## Affected
- Alpine:v3.14: `e2fsprogs` — affected >=0 <1.46.2-r1
- Alpine:v3.15: `e2fsprogs` — affected >=0 <1.46.6-r0
- Alpine:v3.16: `e2fsprogs` — affected >=0 <1.46.6-r0
- Alpine:v3.17: `e2fsprogs` — affected >=0 <1.46.6-r0

## Details
An out-of-bounds read/write vulnerability was found in e2fsprogs 1.46.5. This issue leads to a segmentation fault and possibly arbitrary code execution via a specially crafted filesystem.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1304
