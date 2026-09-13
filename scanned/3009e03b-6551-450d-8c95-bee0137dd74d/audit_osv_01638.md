# [H] ALPINE-CVE-2019-7524

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-7524
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-7524
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.11: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.12: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.13: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.14: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.15: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.16: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.17: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.18: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.19: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.20: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.21: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.22: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.23: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.24: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.6: `dovecot` — affected >=2.3.0 <2.2.36.3-r0
- Alpine:v3.7: `dovecot` — affected >=2.3.0 <2.2.36.3-r0
- Alpine:v3.8: `dovecot` — affected >=2.3.0 <2.3.5.1-r0
- Alpine:v3.9: `dovecot` — affected >=2.3.0 <2.3.5.1-r0

## Details
In Dovecot before 2.2.36.3 and 2.3.x before 2.3.5.1, a local attacker can cause a buffer overflow in the indexer-worker process, which can be used to elevate to root. This occurs because of missing checks in the fts and pop3-uidl components.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-7524
