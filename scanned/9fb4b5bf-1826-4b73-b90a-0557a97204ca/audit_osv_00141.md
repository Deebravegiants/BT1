# [H] ALPINE-CVE-2016-5767

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5767
Ecosystem: Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5767
Type: osv

## Affected
- Alpine:v3.4: `gd` — affected >=0 <2.2.2-r0

## Details
Integer overflow in the gdImageCreate function in gd.c in the GD Graphics Library (aka libgd) before 2.0.34RC1, as used in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8, allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted image dimensions.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5767
