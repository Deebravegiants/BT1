# [M] ALPINE-CVE-2016-6214

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6214
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-08-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6214
Type: osv

## Affected
- Alpine:v3.2: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.3: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.4: `gd` — affected >=0 <2.2.3-r0

## Details
gd_tga.c in the GD Graphics Library (aka libgd) before 2.2.3 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6214
