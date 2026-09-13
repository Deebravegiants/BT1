# [H] ALPINE-CVE-2020-25613

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25613
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25613
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=2.6.0 <2.5.8-r1
- Alpine:v3.11: `ruby` — affected >=2.6.0 <2.6.6-r3
- Alpine:v3.12: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.13: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.14: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.15: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.16: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.17: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.18: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.19: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.20: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.21: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.22: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.23: `ruby` — affected >=2.6.0 <2.7.2-r0
- Alpine:v3.24: `ruby` — affected >=2.6.0 <2.7.2-r0

## Details
An issue was discovered in Ruby through 2.5.8, 2.6.x through 2.6.6, and 2.7.x through 2.7.1. WEBrick, a simple HTTP server bundled with Ruby, had not checked the transfer-encoding header value rigorously. An attacker may potentially exploit this issue to bypass a reverse proxy (which also has a poor header check), which may lead to an HTTP Request Smuggling attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25613
