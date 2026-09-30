# [M] ALPINE-CVE-2019-3814

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-3814
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3814
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.11: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.12: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.13: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.14: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.15: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.16: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.17: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.18: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.19: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.20: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.21: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.22: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.23: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.24: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.6: `dovecot` — affected >=1.1.0 <2.2.36.1-r0
- Alpine:v3.7: `dovecot` — affected >=1.1.0 <2.2.36.1-r0
- Alpine:v3.8: `dovecot` — affected >=1.1.0 <2.3.4.1-r0
- Alpine:v3.9: `dovecot` — affected >=1.1.0 <2.3.4.1-r0

## Details
It was discovered that Dovecot before versions 2.2.36.1 and 2.3.4.1 incorrectly handled client certificates. A remote attacker in possession of a valid certificate with an empty username field could possibly use this issue to impersonate other users.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3814
