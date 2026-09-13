# [H] ALPINE-CVE-2017-8073

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8073
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8073
Type: osv

## Affected
- Alpine:v3.2: `weechat` — affected >=0 <1.2-r1
- Alpine:v3.3: `weechat` — affected >=0 <1.3-r4
- Alpine:v3.4: `weechat` — affected >=0 <1.5-r2
- Alpine:v3.5: `weechat` — affected >=0 <1.6.0-r1
- Alpine:v3.6: `weechat` — affected >=0 <1.7.1-r0
- Alpine:v3.7: `weechat` — affected >=0 <1.7.1-r0
- Alpine:v3.8: `weechat` — affected >=0 <1.7.1-r0
- Alpine:v3.9: `weechat` — affected >=0 <1.7.1-r0

## Details
WeeChat before 1.7.1 allows a remote crash by sending a filename via DCC to the IRC plugin. This occurs in the irc_ctcp_dcc_filename_without_quotes function during quote removal, with a buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8073
