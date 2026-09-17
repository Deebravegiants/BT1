# [C] ALPINE-CVE-2020-7247

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-7247
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-7247
Type: osv

## Affected
- Alpine:v3.11: `opensmtpd` — affected >=0 <6.6.2p1-r0
- Alpine:v3.12: `opensmtpd` — affected >=0 <6.6.2p1-r0
- Alpine:v3.13: `opensmtpd` — affected >=0 <6.6.2p1-r0
- Alpine:v3.14: `opensmtpd` — affected >=0 <6.6.2p1-r0
- Alpine:v3.15: `opensmtpd` — affected >=0 <6.6.2p1-r0
- Alpine:v3.16: `opensmtpd` — affected >=0 <6.6.2p1-r0

## Details
smtp_mailaddr in smtp_session.c in OpenSMTPD 6.6, as used in OpenBSD 6.6 and other products, allows remote attackers to execute arbitrary commands as root via a crafted SMTP session, as demonstrated by shell metacharacters in a MAIL FROM field. This affects the "uncommented" default configuration. The issue exists because of an incorrect return value upon failure of input validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-7247
