# [M] ALPINE-CVE-2016-5321

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-5321
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5321
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The DumpModeDecode function in libtiff 4.0.6 and earlier allows attackers to cause a denial of service (invalid read and crash) via a crafted tiff image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5321
