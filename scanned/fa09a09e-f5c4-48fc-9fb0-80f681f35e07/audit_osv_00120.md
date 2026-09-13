# [C] ALPINE-CVE-2016-5116

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-5116
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5116
Type: osv

## Affected
- Alpine:v3.2: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.3: `gd` — affected >=0 <2.2.1-r2

## Details
gd_xbm.c in the GD Graphics Library (aka libgd) before 2.2.0, as used in certain custom PHP 5.5.x configurations, allows context-dependent attackers to obtain sensitive information from process memory or cause a denial of service (stack-based buffer under-read and application crash) via a long name.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5116
