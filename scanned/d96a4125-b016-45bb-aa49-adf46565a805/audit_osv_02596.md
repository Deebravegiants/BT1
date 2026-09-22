# [M] ALPINE-CVE-2022-34266

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-34266
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-34266
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.3.0-r1

## Details
The libtiff-4.0.3-35.amzn2.0.1 package for LibTIFF on Amazon Linux 2 allows attackers to cause a denial of service (application crash), a different vulnerability than CVE-2022-0562. When processing a malicious TIFF file, an invalid range may be passed as an argument to the memset() function within TIFFFetchStripThing() in tif_dirread.c. This will cause TIFFFetchStripThing() to segfault after use of an uninitialized resource.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-34266
