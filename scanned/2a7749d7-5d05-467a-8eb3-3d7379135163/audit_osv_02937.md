# [M] ALPINE-CVE-2023-51384

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-51384
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-51384
Type: osv

## Affected
- Alpine:v3.16: `openssh` — affected >=8.9 <9.0_p1-r5
- Alpine:v3.17: `openssh` — affected >=8.9 <9.1_p1-r5
- Alpine:v3.19: `openssh` — affected >=8.9 <9.6_p1-r0
- Alpine:v3.20: `openssh` — affected >=8.9 <9.6_p1-r0
- Alpine:v3.21: `openssh` — affected >=8.9 <9.6_p1-r0
- Alpine:v3.22: `openssh` — affected >=8.9 <9.6_p1-r0
- Alpine:v3.23: `openssh` — affected >=8.9 <9.6_p1-r0
- Alpine:v3.24: `openssh` — affected >=8.9 <9.6_p1-r0

## Details
In ssh-agent in OpenSSH before 9.6, certain destination constraints can be incompletely applied. When destination constraints are specified during addition of PKCS#11-hosted private keys, these constraints are only applied to the first key, even if a PKCS#11 token returns multiple keys.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-51384
