# [M] ALPINE-CVE-2017-2625

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-2625
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2625
Type: osv

## Affected
- Alpine:v3.10: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.11: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.12: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.13: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.14: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.15: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.16: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.17: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.18: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.19: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.20: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.21: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.22: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.23: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.24: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.6: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.7: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.8: `libxdmcp` — affected >=0 <1.1.2-r3
- Alpine:v3.9: `libxdmcp` — affected >=0 <1.1.2-r3

## Details
It was discovered that libXdmcp before 1.1.2 including used weak entropy to generate session keys. On a multi-user system using xdmcp, a local attacker could potentially use information available from the process list to brute force the key, allowing them to hijack other users' sessions.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2625
