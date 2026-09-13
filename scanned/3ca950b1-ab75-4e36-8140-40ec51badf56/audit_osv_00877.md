# [H] ALPINE-CVE-2018-1000805

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000805
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000805
Type: osv

## Affected
- Alpine:v3.6: `py-paramiko` — affected >=0 <2.1.6-r0
- Alpine:v3.7: `py-paramiko` — affected >=0 <2.4.2-r0
- Alpine:v3.8: `py-paramiko` — affected >=0 <2.4.2-r0
- Alpine:v3.11: `py3-paramiko` — affected >=0 <2.4.2-r0
- Alpine:v3.12: `py3-paramiko` — affected >=0 <2.4.2-r0
- Alpine:v3.13: `py3-paramiko` — affected >=0 <2.4.2-r0
- Alpine:v3.14: `py3-paramiko` — affected >=0 <2.4.2-r0

## Details
Paramiko version 2.4.1, 2.3.2, 2.2.3, 2.1.5, 2.0.8, 1.18.5, 1.17.6 contains a Incorrect Access Control vulnerability in SSH server that can result in RCE. This attack appear to be exploitable via network connectivity.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000805
