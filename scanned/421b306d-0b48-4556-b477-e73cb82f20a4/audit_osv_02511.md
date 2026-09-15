# [M] ALPINE-CVE-2022-27774

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-27774
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27774
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=4.9 <7.79.1-r1
- Alpine:v3.13: `curl` — affected >=4.9 <7.79.1-r1
- Alpine:v3.14: `curl` — affected >=4.9 <7.79.1-r1
- Alpine:v3.15: `curl` — affected >=4.9 <7.80.0-r1
- Alpine:v3.16: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.17: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.18: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.19: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.20: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.21: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.22: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.23: `curl` — affected >=4.9 <7.83.0-r0
- Alpine:v3.24: `curl` — affected >=4.9 <7.83.0-r0

## Details
An insufficiently protected credentials vulnerability exists in curl 4.9 to and include curl 7.82.0 are affected that could allow an attacker to extract credentials when follows HTTP(S) redirects is used with authentication could leak credentials to other services that exist on different protocols or port numbers.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27774
