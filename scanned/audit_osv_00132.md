# [H] ALPINE-CVE-2016-5323

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5323
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5323
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The _TIFFFax3fillruns function in libtiff before 4.0.6 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted Tiff image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5323
