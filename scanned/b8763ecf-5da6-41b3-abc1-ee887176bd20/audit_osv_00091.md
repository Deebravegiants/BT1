# [C] ALPINE-CVE-2016-3074

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-3074
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3074
Type: osv

## Affected
- Alpine:v3.2: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.3: `gd` — affected >=0 <2.2.1-r2
- Alpine:v3.4: `gd` — affected >=0 <2.2.1-r0

## Details
Integer signedness error in GD Graphics Library 2.1.1 (aka libgd or libgd2) allows remote attackers to cause a denial of service (crash) or potentially execute arbitrary code via crafted compressed gd2 data, which triggers a heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3074
