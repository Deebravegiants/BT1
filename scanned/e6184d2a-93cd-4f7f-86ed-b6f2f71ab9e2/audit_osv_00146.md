# [H] ALPINE-CVE-2016-6128

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6128
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6128
Type: osv

## Affected
- Alpine:v3.2: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.3: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.4: `gd` — affected >=0 <2.2.3-r0

## Details
The gdImageCropThreshold function in gd_crop.c in the GD Graphics Library (aka libgd) before 2.2.3, as used in PHP before 7.0.9, allows remote attackers to cause a denial of service (application crash) via an invalid color index.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6128
