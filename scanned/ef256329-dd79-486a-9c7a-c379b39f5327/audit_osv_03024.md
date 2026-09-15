# [M] ALPINE-CVE-2024-27282

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-27282
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27282
Type: osv

## Affected
- Alpine:v3.16: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.17: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.18: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.19: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.22: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.3.1-r0

## Details
An issue was discovered in Ruby 3.x through 3.3.0. If attacker-supplied data is provided to the Ruby regex compiler, it is possible to extract arbitrary heap data relative to the start of the text, including pointers and sensitive strings. The fixed versions are 3.0.7, 3.1.5, 3.2.4, and 3.3.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27282
