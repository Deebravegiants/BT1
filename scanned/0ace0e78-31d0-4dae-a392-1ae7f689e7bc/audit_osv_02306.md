# [H] ALPINE-CVE-2021-41817

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41817
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41817
Type: osv

## Affected
- Alpine:v3.12: `ruby` — affected >=2.6.0 <2.7.5-r0
- Alpine:v3.13: `ruby` — affected >=2.6.0 <2.7.5-r0
- Alpine:v3.14: `ruby` — affected >=2.6.0 <2.7.5-r0
- Alpine:v3.15: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.16: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.17: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.18: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.19: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.20: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.21: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.22: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.23: `ruby` — affected >=2.6.0 <3.0.3-r0
- Alpine:v3.24: `ruby` — affected >=2.6.0 <3.0.3-r0

## Details
Date.parse in the date gem through 3.2.0 for Ruby allows ReDoS (regular expression Denial of Service) via a long string. The fixed versions are 3.2.1, 3.1.2, 3.0.2, and 2.0.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41817
