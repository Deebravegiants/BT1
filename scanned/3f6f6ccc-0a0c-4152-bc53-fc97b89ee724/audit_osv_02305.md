# [C] ALPINE-CVE-2021-41816

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-41816
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41816
Type: osv

## Affected
- Alpine:v3.12: `ruby` — affected >=0 <2.7.5-r0
- Alpine:v3.13: `ruby` — affected >=0 <2.7.5-r0
- Alpine:v3.14: `ruby` — affected >=0 <2.7.5-r0
- Alpine:v3.15: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.16: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.17: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.18: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.19: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.22: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.0.3-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.0.3-r0

## Details
CGI.escape_html in Ruby before 2.7.5 and 3.x before 3.0.3 has an integer overflow and resultant buffer overflow via a long string on platforms (such as Windows) where size_t and long have different numbers of bytes. This also affects the CGI gem before 0.3.1 for Ruby.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41816
