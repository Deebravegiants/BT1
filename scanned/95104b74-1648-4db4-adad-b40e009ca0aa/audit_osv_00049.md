# [M] ALPINE-CVE-2016-10167

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10167
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10167
Type: osv

## Affected
- Alpine:v3.3: `gd` — affected >=0 <2.2.4-r0
- Alpine:v3.4: `gd` — affected >=0 <2.2.4-r0
- Alpine:v3.5: `gd` — affected >=0 <2.2.4-r0

## Details
The gdImageCreateFromGd2Ctx function in gd_gd2.c in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (application crash) via a crafted image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10167
