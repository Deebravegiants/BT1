# [M] ALPINE-CVE-2019-19722

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19722
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19722
Type: osv

## Affected
- Alpine:v3.11: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.12: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.13: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.14: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.15: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.16: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.17: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.18: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.19: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.20: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.9.2-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.9.2-r0

## Details
In Dovecot before 2.3.9.2, an attacker can crash a push-notification driver with a crafted email when push notifications are used, because of a NULL Pointer Dereference. The email must use a group address as either the sender or the recipient.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19722
