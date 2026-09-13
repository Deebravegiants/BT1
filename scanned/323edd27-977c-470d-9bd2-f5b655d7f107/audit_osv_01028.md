# [H] ALPINE-CVE-2018-16396

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16396
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16396
Type: osv

## Affected
- Alpine:v3.11: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.12: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.13: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.14: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.15: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.16: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.17: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.18: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.19: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.20: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.21: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.22: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.23: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.24: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.4: `ruby` — affected >=2.3.0 <2.3.8-r0
- Alpine:v3.5: `ruby` — affected >=2.3.0 <2.3.8-r0
- Alpine:v3.6: `ruby` — affected >=2.3.0 <2.4.5-r0
- Alpine:v3.7: `ruby` — affected >=2.3.0 <2.4.5-r0
- Alpine:v3.8: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.9: `ruby` — affected >=2.3.0 <2.5.2-r0

## Details
An issue was discovered in Ruby before 2.3.8, 2.4.x before 2.4.5, 2.5.x before 2.5.2, and 2.6.x before 2.6.0-preview3. It does not taint strings that result from unpacking tainted strings with some formats.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16396
