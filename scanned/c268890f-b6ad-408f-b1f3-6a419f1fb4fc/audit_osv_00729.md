# [M] ALPINE-CVE-2017-7485

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7485
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7485
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.11: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.12: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.13: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.14: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.3: `postgresql` — affected >=0 <9.4.12-r0
- Alpine:v3.4: `postgresql` — affected >=0 <9.5.7-r0
- Alpine:v3.5: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.6: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.7: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.8: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.9: `postgresql` — affected >=0 <9.6.3-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <9.6.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <9.6.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <9.6.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <9.6.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <9.6.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <9.6.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <9.6.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <9.6.3-r0

## Details
In PostgreSQL 9.3.x before 9.3.17, 9.4.x before 9.4.12, 9.5.x before 9.5.7, and 9.6.x before 9.6.3, it was found that the PGREQUIRESSL environment variable was no longer enforcing a SSL/TLS connection to a PostgreSQL server. An active Man-in-the-Middle attacker could use this flaw to strip the SSL/TLS protection from a connection between a client and a server.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7485
