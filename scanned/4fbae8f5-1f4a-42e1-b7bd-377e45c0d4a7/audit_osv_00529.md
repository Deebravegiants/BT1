# [H] ALPINE-CVE-2017-15098

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15098
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15098
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.11: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.12: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.13: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.14: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.3: `postgresql` — affected >=0 <9.4.15-r0
- Alpine:v3.4: `postgresql` — affected >=0 <9.5.10-r0
- Alpine:v3.5: `postgresql` — affected >=0 <9.6.6-r0
- Alpine:v3.6: `postgresql` — affected >=0 <9.6.6-r0
- Alpine:v3.7: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.8: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.9: `postgresql` — affected >=0 <10.1-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.1-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.1-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.1-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.1-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.1-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.1-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.1-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.1-r0

## Details
Invalid json_populate_recordset or jsonb_populate_recordset function calls in PostgreSQL 10.x before 10.1, 9.6.x before 9.6.6, 9.5.x before 9.5.10, 9.4.x before 9.4.15, and 9.3.x before 9.3.20 can crash the server or disclose a few bytes of server memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15098
