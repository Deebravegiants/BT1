# [M] ALPINE-CVE-2018-15599

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15599
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15599
Type: osv

## Affected
- Alpine:v3.10: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.11: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.12: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.13: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.14: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.15: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.16: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.17: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.18: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.19: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.20: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.21: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.22: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.23: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.24: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.5: `dropbear` — affected >=0 <2017.75-r1
- Alpine:v3.6: `dropbear` — affected >=0 <2017.75-r1
- Alpine:v3.7: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.8: `dropbear` — affected >=0 <2018.76-r2
- Alpine:v3.9: `dropbear` — affected >=0 <2018.76-r2

## Details
The recv_msg_userauth_request function in svr-auth.c in Dropbear through 2018.76 is prone to a user enumeration vulnerability because username validity affects how fields in SSH_MSG_USERAUTH messages are handled, a similar issue to CVE-2018-15473 in an unrelated codebase.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15599
