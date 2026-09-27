# [H] ALPINE-CVE-2020-12100

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-12100
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12100
Type: osv

## Affected
- Alpine:v3.12: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.13: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.14: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.15: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.16: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.17: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.18: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.19: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.20: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.11.3-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.11.3-r0

## Details
In Dovecot before 2.3.11.3, uncontrolled recursion in submission, lmtp, and lda allows remote attackers to cause a denial of service (resource consumption) via a crafted e-mail message with deeply nested MIME parts.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12100
