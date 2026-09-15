# [M] ALPINE-CVE-2024-10978

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-10978
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-10978
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
Incorrect privilege assignment in PostgreSQL allows a less-privileged application user to view or change different rows from those intended.  An attack requires the application to use SET ROLE, SET SESSION AUTHORIZATION, or an equivalent feature.  The problem arises when an application query uses parameters from the attacker or conveys query results to the attacker.  If that query reacts to current_setting('role') or the current user ID, it may modify or return data as though the session had not used SET ROLE or SET SESSION AUTHORIZATION.  The attacker does not control which incorrect user ID applies.  Query text from less-privileged sources is not a concern here, because SET ROLE and SET SESSION AUTHORIZATION are not sandboxes for unvetted queries.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-10978
