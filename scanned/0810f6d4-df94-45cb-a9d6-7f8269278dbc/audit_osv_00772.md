# [H] ALPINE-CVE-2017-7961

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7961
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7961
Type: osv

## Affected
- Alpine:v3.10: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.11: `libcroco` — affected >=0 <0.6.13-r1
- Alpine:v3.7: `libcroco` — affected >=0 <0.6.12-r1
- Alpine:v3.8: `libcroco` — affected >=0 <0.6.12-r2
- Alpine:v3.9: `libcroco` — affected >=0 <0.6.12-r2

## Details
The cr_tknzr_parse_rgb function in cr-tknzr.c in libcroco 0.6.11 and 0.6.12 has an "outside the range of representable values of type long" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted CSS file. NOTE: third-party analysis reports "This is not a security issue in my view. The conversion surely is truncating the double into a long value, but there is no impact as the value is one of the RGB components.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7961
