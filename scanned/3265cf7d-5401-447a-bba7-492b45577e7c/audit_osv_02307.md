# [H] ALPINE-CVE-2021-41819

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41819
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41819
Type: osv

## Affected
- Alpine:v3.12: `ruby` — affected >=2.7.0 <2.7.5-r0
- Alpine:v3.13: `ruby` — affected >=2.7.0 <2.7.5-r0
- Alpine:v3.14: `ruby` — affected >=2.7.0 <2.7.5-r0
- Alpine:v3.15: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.16: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.17: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.18: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.19: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.20: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.21: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.22: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.23: `ruby` — affected >=2.7.0 <3.0.3-r0
- Alpine:v3.24: `ruby` — affected >=2.7.0 <3.0.3-r0

## Details
CGI::Cookie.parse in Ruby through 2.6.8 mishandles security prefixes in cookie names. This also affects the CGI gem through 0.3.0 for Ruby.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41819
