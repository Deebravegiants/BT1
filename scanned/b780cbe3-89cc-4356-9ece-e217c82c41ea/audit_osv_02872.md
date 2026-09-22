# [M] ALPINE-CVE-2023-4154

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-4154
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4154
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.18.8-r0

## Details
A design flaw was found in Samba's DirSync control implementation, which exposes passwords and secrets in Active Directory to privileged users and Read-Only Domain Controllers (RODCs). This flaw allows RODCs and users possessing the GET_CHANGES right to access all attributes, including sensitive secrets and passwords. Even in a default setup, RODC DC accounts, which should only replicate some passwords, can gain access to all domain secrets, including the vital krbtgt, effectively eliminating the RODC / DC distinction. Furthermore, the vulnerability fails to account for error conditions (fail open), like out-of-memory situations, potentially granting access to secret attributes, even under low-privileged attacker influence.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4154
