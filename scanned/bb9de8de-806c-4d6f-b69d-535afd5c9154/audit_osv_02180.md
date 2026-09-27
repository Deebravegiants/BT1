# [H] ALPINE-CVE-2021-28965

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28965
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28965
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=2.7.0 <2.5.9-r0
- Alpine:v3.11: `ruby` — affected >=2.7.0 <2.6.7-r0
- Alpine:v3.12: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.13: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.14: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.15: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.16: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.17: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.18: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.19: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.20: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.21: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.22: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.23: `ruby` — affected >=2.7.0 <2.7.3-r0
- Alpine:v3.24: `ruby` — affected >=2.7.0 <2.7.3-r0

## Details
The REXML gem before 3.2.5 in Ruby before 2.6.7, 2.7.x before 2.7.3, and 3.x before 3.0.1 does not properly address XML round-trip issues. An incorrect document can be produced after parsing and serializing.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28965
