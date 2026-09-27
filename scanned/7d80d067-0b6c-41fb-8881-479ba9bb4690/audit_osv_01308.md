# [H] ALPINE-CVE-2019-1010057

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-1010057
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1010057
Type: osv

## Affected
- Alpine:v3.10: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.11: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.12: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.13: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.14: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.15: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.16: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.17: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.18: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.19: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.20: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.21: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.22: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.23: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.24: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.7: `nfdump` — affected >=0 <1.6.15-r1
- Alpine:v3.9: `nfdump` — affected >=0 <1.6.18-r0

## Details
nfdump 1.6.16 and earlier is affected by: Buffer Overflow. The impact is: The impact could range from a denial of service to local code execution. The component is: nfx.c:546, nffile_inline.c:83, minilzo.c (redistributed). The attack vector is: nfdump must read and process a specially crafted file. The fixed version is: after commit 9f0fe9563366f62a71d34c92229da3432ec5cf0e.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1010057
