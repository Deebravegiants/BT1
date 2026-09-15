# [H] ALPINE-CVE-2017-11164

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11164
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11164
Type: osv

## Affected
- Alpine:v3.10: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.11: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.12: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.13: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.14: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.15: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.16: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.17: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.18: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.19: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.20: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.21: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.22: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.23: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.24: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.6: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.7: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.8: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.9: `pcre` — affected >=0 <7.8-r0

## Details
In PCRE 8.41, the OP_KETRMAX feature in the match function in pcre_exec.c allows stack exhaustion (uncontrolled recursion) when processing a crafted regular expression.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11164
