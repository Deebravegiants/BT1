# [M] ALPINE-CVE-2017-2626

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-2626
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2626
Type: osv

## Affected
- Alpine:v3.11: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.12: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.13: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.14: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.15: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.16: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.17: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.18: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.19: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.20: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.21: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.22: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.23: `libice` — affected >=0 <1.0.10-r0
- Alpine:v3.24: `libice` — affected >=0 <1.0.10-r0

## Details
It was discovered that libICE before 1.0.9-8 used a weak entropy to generate keys. A local attacker could potentially use this flaw for session hijacking using the information available from the process list.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2626
