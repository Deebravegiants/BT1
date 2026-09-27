# [H] ALPINE-CVE-2017-12150

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12150
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12150
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.11: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.12: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.13: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.14: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.15: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.16: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.17: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.18: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.19: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.20: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.21: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.22: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.23: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.24: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.4: `samba` — affected >=3.0.25 <4.4.16-r0
- Alpine:v3.5: `samba` — affected >=3.0.25 <4.5.14-r0
- Alpine:v3.6: `samba` — affected >=3.0.25 <4.6.8-r0
- Alpine:v3.7: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.8: `samba` — affected >=3.0.25 <4.7.0-r0
- Alpine:v3.9: `samba` — affected >=3.0.25 <4.7.0-r0

## Details
It was found that samba before 4.4.16, 4.5.x before 4.5.14, and 4.6.x before 4.6.8 did not enforce "SMB signing" when certain configuration options were enabled. A remote attacker could launch a man-in-the-middle attack and retrieve information in plain-text.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12150
