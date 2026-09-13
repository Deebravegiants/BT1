# [H] ALPINE-CVE-2019-10164

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10164
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10164
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.11: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.12: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.13: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.7: `postgresql` — affected >=10.0 <10.9-r0
- Alpine:v3.8: `postgresql` — affected >=10.0 <10.9-r0
- Alpine:v3.9: `postgresql` — affected >=10.0 <11.4-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <11.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <11.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <11.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <11.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <11.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <11.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <11.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <11.4-r0

## Details
PostgreSQL versions 10.x before 10.9 and versions 11.x before 11.4 are vulnerable to a stack-based buffer overflow. Any authenticated user can overflow a stack-based buffer by changing the user's own password to a purpose-crafted value. This often suffices to execute arbitrary code as the PostgreSQL operating system account.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10164
