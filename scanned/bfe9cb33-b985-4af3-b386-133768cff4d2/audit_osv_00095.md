# [M] ALPINE-CVE-2016-3186

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3186
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3186
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
Buffer overflow in the readextension function in gif2tiff.c in LibTIFF 4.0.6 allows remote attackers to cause a denial of service (application crash) via a crafted GIF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3186
