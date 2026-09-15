# [H] ALPINE-CVE-2017-14727

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14727
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14727
Type: osv

## Affected
- Alpine:v3.5: `weechat` — affected >=0 <1.6.0-r2
- Alpine:v3.6: `weechat` — affected >=0 <1.7.1-r2
- Alpine:v3.7: `weechat` — affected >=0 <1.9.1-r0
- Alpine:v3.8: `weechat` — affected >=0 <1.9.1-r0
- Alpine:v3.9: `weechat` — affected >=0 <1.9.1-r0

## Details
logger.c in the logger plugin in WeeChat before 1.9.1 allows a crash via strftime date/time specifiers, because a buffer is not initialized.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14727
