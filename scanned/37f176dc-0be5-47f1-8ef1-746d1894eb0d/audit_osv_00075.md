# [M] ALPINE-CVE-2016-2124

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2124
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2124
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=3.0.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=3.0.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.16: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.17: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.18: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.19: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.20: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.21: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.22: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.23: `samba` — affected >=3.0.0 <4.15.2-r0
- Alpine:v3.24: `samba` — affected >=3.0.0 <4.15.2-r0

## Details
A flaw was found in the way samba implemented SMB1 authentication. An attacker could use this flaw to retrieve the plaintext password sent over the wire even if Kerberos authentication was required.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2124
