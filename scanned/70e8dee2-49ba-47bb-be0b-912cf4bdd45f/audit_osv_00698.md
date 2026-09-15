# [H] ALPINE-CVE-2017-6362

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6362
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6362
Type: osv

## Affected
- Alpine:v3.4: `gd` — affected >=0 <2.2.5-r0
- Alpine:v3.5: `gd` — affected >=0 <2.2.5-r0
- Alpine:v3.6: `gd` — affected >=0 <2.2.5-r0

## Details
Double free vulnerability in the gdImagePngPtr function in libgd2 before 2.2.5 allows remote attackers to cause a denial of service via vectors related to a palette with no colors.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6362
