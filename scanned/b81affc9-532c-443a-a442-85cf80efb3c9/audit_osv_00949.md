# [M] ALPINE-CVE-2018-12435

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12435
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 5.9 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12435
Type: osv

## Affected
- Alpine:v3.11: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.12: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.13: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.14: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.15: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.16: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.17: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.18: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.19: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.20: `botan` — affected >=2.5.0 <2.7.0-r0
- Alpine:v3.21: `botan` — affected >=2.5.0 <2.7.0-r0

## Details
Botan 2.5.0 through 2.6.0 before 2.7.0 allows a memory-cache side-channel attack on ECDSA signatures, aka the Return Of the Hidden Number Problem or ROHNP, related to dsa/dsa.cpp, ec_group/ec_group.cpp, and ecdsa/ecdsa.cpp. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12435
