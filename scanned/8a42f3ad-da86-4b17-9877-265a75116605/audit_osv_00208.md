# [M] ALPINE-CVE-2016-6906

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6906
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6906
Type: osv

## Affected
- Alpine:v3.3: `gd` — affected >=0 <2.2.4-r0
- Alpine:v3.4: `gd` — affected >=0 <2.2.4-r0
- Alpine:v3.5: `gd` — affected >=0 <2.2.4-r0

## Details
The read_image_tga function in gd_tga.c in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file, related to the decompression buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6906
