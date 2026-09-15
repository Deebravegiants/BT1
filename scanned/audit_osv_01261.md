# [C] ALPINE-CVE-2018-7750

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-7750
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7750
Type: osv

## Affected
- Alpine:v3.11: `py3-paramiko` — affected >=0 <2.4.1-r0
- Alpine:v3.12: `py3-paramiko` — affected >=0 <2.4.1-r0
- Alpine:v3.13: `py3-paramiko` — affected >=0 <2.4.1-r0
- Alpine:v3.14: `py3-paramiko` — affected >=0 <2.4.1-r0

## Details
transport.py in the SSH server implementation of Paramiko before 1.17.6, 1.18.x before 1.18.5, 2.0.x before 2.0.8, 2.1.x before 2.1.5, 2.2.x before 2.2.3, 2.3.x before 2.3.2, and 2.4.x before 2.4.1 does not properly check whether authentication is completed before processing other requests, as demonstrated by channel-open. A customized SSH client can simply skip the authentication step.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7750
