# [M] ALPINE-CVE-2021-4122

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-4122
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-4122
Type: osv

## Affected
- Alpine:v3.12: `cryptsetup` — affected >=2.4.0 <2.3.7-r0
- Alpine:v3.13: `cryptsetup` — affected >=2.4.0 <2.3.7-r0
- Alpine:v3.14: `cryptsetup` — affected >=2.4.0 <2.3.7-r0
- Alpine:v3.15: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.16: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.17: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.18: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.19: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.20: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.21: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.22: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.23: `cryptsetup` — affected >=2.4.0 <2.4.3-r0
- Alpine:v3.24: `cryptsetup` — affected >=2.4.0 <2.4.3-r0

## Details
It was found that a specially crafted LUKS header could trick cryptsetup into disabling encryption during the recovery of the device. An attacker with physical access to the medium, such as a flash disk, could use this flaw to force a user into permanently disabling the encryption layer of that medium.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-4122
