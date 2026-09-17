# [H] ALPINE-CVE-2023-39417

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-39417
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-39417
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=11.0 <13.12-r0
- Alpine:v3.14: `postgresql` — affected >=11.0 <13.12-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.12-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.12-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.4-r0

## Details
IN THE EXTENSION SCRIPT, a SQL Injection vulnerability was found in PostgreSQL if it uses @extowner@, @extschema@, or @extschema:...@ inside a quoting construct (dollar quoting, '', or ""). If an administrator has installed files of a vulnerable, trusted, non-bundled extension, an attacker with database-level CREATE privilege can execute arbitrary code as the bootstrap superuser.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-39417
