# [H] ALPINE-CVE-2017-14461

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14461
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14461
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.11: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.12: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.13: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.14: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.15: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.16: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.17: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.18: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.19: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.20: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.7: `dovecot` — affected >=0 <2.2.34-r0
- Alpine:v3.8: `dovecot` — affected >=0 <2.3.1-r0
- Alpine:v3.9: `dovecot` — affected >=0 <2.3.1-r0

## Details
A specially crafted email delivered over SMTP and passed on to Dovecot by MTA can trigger an out of bounds read resulting in potential sensitive information disclosure and denial of service. In order to trigger this vulnerability, an attacker needs to send a specially crafted email message to the server.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14461
