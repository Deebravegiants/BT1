# [C] ALPINE-CVE-2016-7568

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7568
Ecosystem: Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7568
Type: osv

## Affected
- Alpine:v3.4: `gd` — affected >=0 <2.2.3-r1

## Details
Integer overflow in the gdImageWebpCtx function in gd_webp.c in the GD Graphics Library (aka libgd) through 2.2.3, as used in PHP through 7.0.11, allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via crafted imagewebp and imagedestroy calls.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7568
