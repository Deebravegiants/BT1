# [M] ALPINE-CVE-2019-15845

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-15845
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15845
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=2.4.0 <2.5.7-r0
- Alpine:v3.11: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.12: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.13: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.14: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.15: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.16: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.17: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.18: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.19: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.20: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.21: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.22: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.23: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.24: `ruby` — affected >=2.4.0 <2.6.5-r0
- Alpine:v3.7: `ruby` — affected >=2.4.0 <2.4.10-r0
- Alpine:v3.8: `ruby` — affected >=2.4.0 <2.5.7-r0
- Alpine:v3.9: `ruby` — affected >=2.4.0 <2.5.7-r0

## Details
Ruby through 2.4.7, 2.5.x through 2.5.6, and 2.6.x through 2.6.4 mishandles path checking within File.fnmatch functions.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15845
