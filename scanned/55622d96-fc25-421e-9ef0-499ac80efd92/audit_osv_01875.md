# [H] ALPINE-CVE-2020-25097

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25097
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25097
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=2.0 <4.14-r0
- Alpine:v3.11: `squid` — affected >=2.0 <4.14-r0
- Alpine:v3.12: `squid` — affected >=2.0 <4.14-r0
- Alpine:v3.13: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.14: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.15: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.16: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.17: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.18: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.19: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.20: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.21: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.22: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.23: `squid` — affected >=2.0 <5.0.5-r0
- Alpine:v3.24: `squid` — affected >=2.0 <5.0.5-r0

## Details
An issue was discovered in Squid through 4.13 and 5.x through 5.0.4. Due to improper input validation, it allows a trusted client to perform HTTP Request Smuggling and access services otherwise forbidden by the security controls. This occurs for certain uri_whitespace configuration settings.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25097
