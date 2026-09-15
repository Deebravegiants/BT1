# [H] ALPINE-CVE-2017-15132

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15132
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15132
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.11: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.12: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.13: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.14: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.15: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.16: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.17: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.18: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.19: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.20: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.21: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.22: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.23: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.24: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.7: `dovecot` — affected >=2.0.0 <2.2.34-r0
- Alpine:v3.8: `dovecot` — affected >=2.0.0 <2.3.1-r0
- Alpine:v3.9: `dovecot` — affected >=2.0.0 <2.3.1-r0

## Details
A flaw was found in dovecot 2.0 up to 2.2.33 and 2.3.0. An abort of SASL authentication results in a memory leak in dovecot's auth client used by login processes. The leak has impact in high performance configuration where same login processes are reused and can cause the process to crash due to memory exhaustion.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15132
