# [C] ALPINE-CVE-2020-1946

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-1946
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1946
Type: osv

## Affected
- Alpine:v3.10: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.11: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.12: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.13: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.14: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.15: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.16: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.17: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.18: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.19: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.20: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.21: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.22: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.23: `spamassassin` — affected >=0 <3.4.5-r0
- Alpine:v3.24: `spamassassin` — affected >=0 <3.4.5-r0

## Details
In Apache SpamAssassin before 3.4.5, malicious rule configuration (.cf) files can be configured to run system commands without any output or errors. With this, exploits can be injected in a number of scenarios. In addition to upgrading to SA version 3.4.5, users should only use update channels or 3rd party .cf files from trusted places.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1946
