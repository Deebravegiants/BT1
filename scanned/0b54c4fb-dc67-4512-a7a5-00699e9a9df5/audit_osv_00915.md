# [C] ALPINE-CVE-2018-1115

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-1115
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1115
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.11: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.12: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.13: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.4: `postgresql` — affected >=10.0 <9.5.13-r0
- Alpine:v3.5: `postgresql` — affected >=10.0 <9.6.9-r0
- Alpine:v3.6: `postgresql` — affected >=10.0 <9.6.9-r0
- Alpine:v3.7: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.8: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.9: `postgresql` — affected >=10.0 <10.4-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.4-r0

## Details
postgresql before versions 10.4, 9.6.9 is vulnerable in the adminpack extension, the pg_catalog.pg_logfile_rotate() function doesn't follow the same ACLs than pg_rorate_logfile. If the adminpack is added to a database, an attacker able to connect to it could exploit this to force log rotation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1115
