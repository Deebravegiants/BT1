# [H] ALPINE-CVE-2019-14855

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14855
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14855
Type: osv

## Affected
- Alpine:v3.10: `gnupg` — affected >=0 <2.2.19-r0
- Alpine:v3.11: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.12: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.13: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.14: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.15: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.16: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.17: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.18: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.19: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.20: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.21: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.22: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.23: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.24: `gnupg` — affected >=0 <2.2.18-r0
- Alpine:v3.8: `gnupg` — affected >=0 <2.2.19-r0
- Alpine:v3.9: `gnupg` — affected >=0 <2.2.19-r0

## Details
A flaw was found in the way certificate signatures could be forged using collisions found in the SHA-1 algorithm. An attacker could use this weakness to create forged certificate signatures. This issue affects GnuPG versions before 2.2.18.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14855
