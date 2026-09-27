# [M] ALPINE-CVE-2020-24386

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-24386
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-24386
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.11: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.12: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.13: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.14: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.15: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.16: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.17: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.18: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.19: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.20: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.21: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.22: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.23: `dovecot` — affected >=2.2.26 <2.3.13-r0
- Alpine:v3.24: `dovecot` — affected >=2.2.26 <2.3.13-r0

## Details
An issue was discovered in Dovecot before 2.3.13. By using IMAP IDLE, an authenticated attacker can trigger unhibernation via attacker-controlled parameters, leading to access to other users' email messages (and path disclosure).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-24386
