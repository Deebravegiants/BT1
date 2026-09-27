# [M] ALPINE-CVE-2019-3880

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-3880
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3880
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.11: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.12: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.13: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.14: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.15: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.16: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.17: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.18: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.19: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.20: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.21: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.22: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.23: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.24: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.6: `samba` — affected >=3.2.0 <4.6.16-r1
- Alpine:v3.7: `samba` — affected >=3.2.0 <4.7.6-r3
- Alpine:v3.8: `samba` — affected >=3.2.0 <4.8.11-r0
- Alpine:v3.9: `samba` — affected >=3.2.0 <4.8.11-r0

## Details
A flaw was found in the way samba implemented an RPC endpoint emulating the Windows registry service API. An unprivileged attacker could use this flaw to create a new registry hive file anywhere they have unix permissions which could lead to creation of a new file in the Samba share. Versions before 4.8.11, 4.9.6 and 4.10.2 are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3880
