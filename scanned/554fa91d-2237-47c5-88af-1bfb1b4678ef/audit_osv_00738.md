# [H] ALPINE-CVE-2017-7547

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7547
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7547
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.11: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.12: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.13: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.14: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.3: `postgresql` — affected >=0 <9.4.13-r0
- Alpine:v3.4: `postgresql` — affected >=0 <9.5.8-r0
- Alpine:v3.5: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.6: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.7: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.8: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.9: `postgresql` — affected >=0 <9.6.4-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <9.6.4-r0

## Details
PostgreSQL versions before 9.2.22, 9.3.18, 9.4.13, 9.5.8 and 9.6.4 are vulnerable to authorization flaw allowing remote authenticated attackers to retrieve passwords from the user mappings defined by the foreign server owners without actually having the privileges to do so.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7547
