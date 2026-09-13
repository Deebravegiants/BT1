# [M] ALPINE-CVE-2021-33515

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-33515
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33515
Type: osv

## Affected
- Alpine:v3.11: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.12: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.13: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.14: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.15: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.16: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.17: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.18: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.19: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.20: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.15-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.15-r0

## Details
The submission service in Dovecot before 2.3.15 allows STARTTLS command injection in lib-smtp. Sensitive information can be redirected to an attacker-controlled address.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33515
