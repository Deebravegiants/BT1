# [H] ALPINE-CVE-2024-10979

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-10979
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-10979
Type: osv

## Affected
- Alpine:v3.17: `postgresql14` — affected >=0 <14.14-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.14-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.9-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.9-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.9-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.9-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.5-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.5-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.5-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.5-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.1-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.1-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.1-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.1-r0

## Details
Incorrect control of environment variables in PostgreSQL PL/Perl allows an unprivileged database user to change sensitive process environment variables (e.g. PATH).  That often suffices to enable arbitrary code execution, even if the attacker lacks a database server operating system user.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-10979
