# [H] ALPINE-CVE-2022-28739

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-28739
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28739
Type: osv

## Affected
- Alpine:v3.12: `ruby` — affected >=2.7.0 <2.7.6-r0
- Alpine:v3.13: `ruby` — affected >=2.7.0 <2.7.6-r0
- Alpine:v3.14: `ruby` — affected >=2.7.0 <2.7.6-r0
- Alpine:v3.15: `ruby` — affected >=2.7.0 <3.0.4-r0
- Alpine:v3.16: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.17: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.18: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.19: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.20: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.21: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.22: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.23: `ruby` — affected >=2.7.0 <3.1.2-r0
- Alpine:v3.24: `ruby` — affected >=2.7.0 <3.1.2-r0

## Details
There is a buffer over-read in Ruby before 2.6.10, 2.7.x before 2.7.6, 3.x before 3.0.4, and 3.1.x before 3.1.2. It occurs in String-to-Float conversion, including Kernel#Float and String#to_f.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28739
