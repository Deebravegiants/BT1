# [M] ALPINE-CVE-2022-2057

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2057
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2057
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.4.0-r1

## Details
Divide By Zero error in tiffcrop in libtiff 4.4.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit f3a5e010.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2057
