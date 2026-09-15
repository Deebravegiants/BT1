# [M] ALPINE-CVE-2017-7960

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7960
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7960
Type: osv

## Affected
- Alpine:v3.10: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.11: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.7: `libcroco` — affected >=0 <0.6.12-r1
- Alpine:v3.8: `libcroco` — affected >=0 <0.6.12-r2
- Alpine:v3.9: `libcroco` — affected >=0 <0.6.12-r2

## Details
The cr_input_new_from_uri function in cr-input.c in libcroco 0.6.11 and 0.6.12 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted CSS file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7960
