# [H] ALPINE-CVE-2020-8517

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8517
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8517
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=0 <4.10-r0
- Alpine:v3.11: `squid` — affected >=0 <4.10-r0
- Alpine:v3.12: `squid` — affected >=0 <4.10-r0
- Alpine:v3.13: `squid` — affected >=0 <4.10-r0
- Alpine:v3.14: `squid` — affected >=0 <4.10-r0
- Alpine:v3.15: `squid` — affected >=0 <4.10-r0
- Alpine:v3.16: `squid` — affected >=0 <4.10-r0
- Alpine:v3.17: `squid` — affected >=0 <4.10-r0
- Alpine:v3.18: `squid` — affected >=0 <4.10-r0
- Alpine:v3.19: `squid` — affected >=0 <4.10-r0
- Alpine:v3.20: `squid` — affected >=0 <4.10-r0
- Alpine:v3.21: `squid` — affected >=0 <4.10-r0
- Alpine:v3.22: `squid` — affected >=0 <4.10-r0
- Alpine:v3.23: `squid` — affected >=0 <4.10-r0
- Alpine:v3.24: `squid` — affected >=0 <4.10-r0
- Alpine:v3.8: `squid` — affected >=0 <3.5.27-r4
- Alpine:v3.9: `squid` — affected >=0 <4.10-r0

## Details
An issue was discovered in Squid before 4.10. Due to incorrect input validation, the NTLM authentication credentials parser in ext_lm_group_acl may write to memory outside the credentials buffer. On systems with memory access protections, this can result in the helper process being terminated unexpectedly. This leads to the Squid process also terminating and a denial of service for all clients using the proxy.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8517
