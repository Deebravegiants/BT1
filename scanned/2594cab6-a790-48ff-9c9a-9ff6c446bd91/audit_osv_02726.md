# [H] ALPINE-CVE-2022-45061

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-45061
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-45061
Type: osv

## Affected
- Alpine:v3.14: `python3` — affected >=0 <3.9.16-r0
- Alpine:v3.15: `python3` — affected >=0 <3.9.16-r0
- Alpine:v3.16: `python3` — affected >=0 <3.10.9-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.9-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.20: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.21: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.22: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.23: `python3` — affected >=0 <3.11.1-r0
- Alpine:v3.24: `python3` — affected >=0 <3.11.1-r0

## Details
An issue was discovered in Python before 3.11.1. An unnecessary quadratic algorithm exists in one path when processing some inputs to the IDNA (RFC 3490) decoder, such that a crafted, unreasonably long name being presented to the decoder could lead to a CPU denial of service. Hostnames are often supplied by remote servers that could be controlled by a malicious actor; in such a scenario, they could trigger excessive CPU consumption on the client attempting to make use of an attacker-supplied supposed hostname. For example, the attack payload could be placed in the Location header of an HTTP response with status code 302. A fix is planned in 3.11.1, 3.10.9, 3.9.16, 3.8.16, and 3.7.16.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-45061
