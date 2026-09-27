# [H] ALPINE-CVE-2020-25275

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25275
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25275
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.11: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.12: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.13: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.14: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.15: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.16: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.17: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.18: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.19: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.20: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.13-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.13-r0

## Details
Dovecot before 2.3.13 has Improper Input Validation in lda, lmtp, and imap, leading to an application crash via a crafted email message with certain choices for ten thousand MIME parts.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25275
