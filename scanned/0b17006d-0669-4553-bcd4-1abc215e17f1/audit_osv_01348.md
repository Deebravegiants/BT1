# [C] ALPINE-CVE-2019-11500

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-11500
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11500
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.11: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.12: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.13: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.14: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.15: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.16: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.17: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.18: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.19: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.20: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.21: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.22: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.23: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.24: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.7: `dovecot` — affected >=2.3.0 <2.2.36.4-r0
- Alpine:v3.8: `dovecot` — affected >=2.3.0 <2.3.7.2-r0
- Alpine:v3.9: `dovecot` — affected >=2.3.0 <2.3.7.2-r0

## Details
In Dovecot before 2.2.36.4 and 2.3.x before 2.3.7.2 (and Pigeonhole before 0.5.7.2), protocol processing can fail for quoted strings. This occurs because '\0' characters are mishandled, and can lead to out-of-bounds writes and remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11500
