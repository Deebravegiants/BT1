# [C] ALPINE-CVE-2018-16850

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-16850
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16850
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.11: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.12: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.13: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.9: `postgresql` — affected >=10.0 <11.1-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <11.1-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <11.1-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <11.1-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <11.1-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <11.1-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <11.1-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <11.1-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <11.1-r0

## Details
postgresql before versions 11.1, 10.6 is vulnerable to a to SQL injection in pg_upgrade and pg_dump via CREATE TRIGGER ... REFERENCING. Using a purpose-crafted trigger definition, an attacker can cause arbitrary SQL statements to run, with superuser privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16850
