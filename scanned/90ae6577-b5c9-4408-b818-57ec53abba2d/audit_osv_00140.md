# [H] ALPINE-CVE-2016-5766

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5766
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5766
Type: osv

## Affected
- Alpine:v3.2: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.3: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.4: `gd` — affected >=0 <2.2.3-r0

## Details
Integer overflow in the _gd2GetHeader function in gd_gd2.c in the GD Graphics Library (aka libgd) before 2.2.3, as used in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8, allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via crafted chunk dimensions in an image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5766
