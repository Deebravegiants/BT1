# [H] ALPINE-CVE-2021-32066

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32066
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32066
Type: osv

## Affected
- Alpine:v3.11: `ruby` — affected >=2.6.0 <2.6.8-r0
- Alpine:v3.12: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.13: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.14: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.15: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.16: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.17: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.18: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.19: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.20: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.21: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.22: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.23: `ruby` — affected >=2.6.0 <2.7.4-r0
- Alpine:v3.24: `ruby` — affected >=2.6.0 <2.7.4-r0

## Details
An issue was discovered in Ruby through 2.6.7, 2.7.x through 2.7.3, and 3.x through 3.0.1. Net::IMAP does not raise an exception when StartTLS fails with an an unknown response, which might allow man-in-the-middle attackers to bypass the TLS protections by leveraging a network position between the client and the registry to block the StartTLS command, aka a "StartTLS stripping attack."

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32066
