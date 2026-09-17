# [H] ALPINE-CVE-2021-33621

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-33621
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33621
Type: osv

## Affected
- Alpine:v3.14: `ruby` — affected >=2.7.0 <2.7.7-r0
- Alpine:v3.15: `ruby` — affected >=2.7.0 <3.0.5-r0
- Alpine:v3.16: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.17: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.18: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.19: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.20: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.21: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.22: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.23: `ruby` — affected >=2.7.0 <3.1.3-r0
- Alpine:v3.24: `ruby` — affected >=2.7.0 <3.1.3-r0

## Details
The cgi gem before 0.1.0.2, 0.2.x before 0.2.2, and 0.3.x before 0.3.5 for Ruby allows HTTP response splitting. This is relevant to applications that use untrusted user input either to generate an HTTP response or to create a CGI::Cookie object.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33621
