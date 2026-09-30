# [M] ALPINE-CVE-2016-9273

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9273
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9273
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
tiffsplit in libtiff 4.0.6 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file, related to changing td_nstrips in TIFF_STRIPCHOP mode.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9273
