# [H] ALPINE-CVE-2020-1931

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-1931
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1931
Type: osv

## Affected
- Alpine:v3.10: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.11: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.12: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.13: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.14: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.15: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.16: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.17: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.18: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.19: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.20: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.21: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.22: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.23: `spamassassin` — affected >=0 <3.4.4-r0
- Alpine:v3.24: `spamassassin` — affected >=0 <3.4.4-r0

## Details
A command execution issue was found in Apache SpamAssassin prior to 3.4.3. Carefully crafted nefarious Configuration (.cf) files can be configured to run system commands similar to CVE-2018-11805. This issue is less stealthy and attempts to exploit the issue will throw warnings. Thanks to Damian Lukowski at credativ for reporting the issue ethically. With this bug unpatched, exploits can be injected in a number of scenarios though doing so remotely is difficult. In addition to upgrading to SA 3.4.4, we again recommend that users should only use update channels or 3rd party .cf files from trusted places.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1931
