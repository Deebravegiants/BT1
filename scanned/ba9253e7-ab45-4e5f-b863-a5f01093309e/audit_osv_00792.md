# [M] ALPINE-CVE-2017-8834

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-8834
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8834
Type: osv

## Affected
- Alpine:v3.10: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.11: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.7: `libcroco` — affected >=0 <0.6.12-r1
- Alpine:v3.8: `libcroco` — affected >=0 <0.6.12-r2
- Alpine:v3.9: `libcroco` — affected >=0 <0.6.12-r2

## Details
The cr_tknzr_parse_comment function in cr-tknzr.c in libcroco 0.6.12 allows remote attackers to cause a denial of service (memory allocation error) via a crafted CSS file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8834
