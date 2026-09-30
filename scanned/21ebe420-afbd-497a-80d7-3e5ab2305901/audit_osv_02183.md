# [M] ALPINE-CVE-2021-29157

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-29157
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29157
Type: osv

## Affected
- Alpine:v3.11: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.12: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.13: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.14: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.15: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.16: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.17: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.18: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.19: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.20: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.21: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.22: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.23: `dovecot` — affected >=2.3.11 <2.3.15-r0
- Alpine:v3.24: `dovecot` — affected >=2.3.11 <2.3.15-r0

## Details
Dovecot before 2.3.15 allows ../ Path Traversal. An attacker with access to the local filesystem can trick OAuth2 authentication into using an HS256 validation key from an attacker-controlled location. This occurs during use of local JWT validation with the posix fs driver.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29157
