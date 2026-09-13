# [H] ALPINE-CVE-2022-40023

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40023
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40023
Type: osv

## Affected
- Alpine:v3.16: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.17: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.18: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.19: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.20: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.21: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.22: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.23: `py3-mako` — affected >=0 <1.2.2-r0
- Alpine:v3.24: `py3-mako` — affected >=0 <1.2.2-r0

## Details
Sqlalchemy mako before 1.2.2 is vulnerable to Regular expression Denial of Service when using the Lexer class to parse. This also affects babelplugin and linguaplugin.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40023
