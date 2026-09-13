# [M] ALPINE-CVE-2020-7957

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-7957
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-7957
Type: osv

## Affected
- Alpine:v3.10: `dovecot` — affected >=2.3.9 <2.3.10.1-r0
- Alpine:v3.11: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.12: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.13: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.14: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.15: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.16: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.17: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.18: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.19: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.20: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.21: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.22: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.23: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.24: `dovecot` — affected >=2.3.9 <2.3.9.3-r0
- Alpine:v3.8: `dovecot` — affected >=2.3.9 <2.3.10.1-r0
- Alpine:v3.9: `dovecot` — affected >=2.3.9 <2.3.10.1-r0

## Details
The IMAP and LMTP components in Dovecot 2.3.9 before 2.3.9.3 mishandle snippet generation when many characters must be read to compute the snippet and a trailing > character exists. This causes a denial of service in which the recipient cannot read all of their messages.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-7957
