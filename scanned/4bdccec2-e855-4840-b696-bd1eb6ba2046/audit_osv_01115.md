# [M] ALPINE-CVE-2018-20187

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20187
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20187
Type: osv

## Affected
- Alpine:v3.11: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.12: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.13: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.14: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.15: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.16: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.17: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.18: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.19: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.20: `botan` — affected >=0 <2.9.0-r0
- Alpine:v3.21: `botan` — affected >=0 <2.9.0-r0

## Details
A side-channel issue was discovered in Botan before 2.9.0. An attacker capable of precisely measuring the time taken for ECC key generation may be able to derive information about the high bits of the secret key, as the function to derive the public point from the secret scalar uses an unblinded Montgomery ladder whose loop iteration count depends on the bitlength of the secret. This issue affects only key generation, not ECDSA signatures or ECDH key agreement.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20187
