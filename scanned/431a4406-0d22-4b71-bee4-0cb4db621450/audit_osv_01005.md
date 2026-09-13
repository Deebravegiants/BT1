# [M] ALPINE-CVE-2018-15120

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15120
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15120
Type: osv

## Affected
- Alpine:v3.7: `pango` — affected >=1.40.8 <1.40.14-r1
- Alpine:v3.8: `pango` — affected >=1.40.8 <1.40.14-r1

## Details
libpango in Pango 1.40.8 through 1.42.3, as used in hexchat and other products, allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via crafted text with invalid Unicode sequences.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15120
