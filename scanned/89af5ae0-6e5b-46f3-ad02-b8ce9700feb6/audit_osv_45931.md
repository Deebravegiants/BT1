# [M] JLSEC-2026-49

## Summary
Severity: Medium
Advisory: JLSEC-2026-49
Ecosystem: Julia
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-49
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.8.0+0

## Details
Incorrect privilege assignment in PostgreSQL allows a less-privileged application user to view or change different rows from those intended.  An attack requires the application to use SET ROLE, SET SESSION AUTHORIZATION, or an equivalent feature.  The problem arises when an application query uses parameters from the attacker or conveys query results to the attacker.  If that query reacts to `current_setting('role')` or the current user ID, it may modify or return data as though the session had not used SET ROLE or SET SESSION AUTHORIZATION.  The attacker does not control which incorrect user ID applies.  Query text from less-privileged sources is not a concern here, because SET ROLE and SET SESSION AUTHORIZATION are not sandboxes for unvetted queries.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00011.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00018.html
- https://www.postgresql.org/message-id/173171334532.1547978.1518068370217143844%40wrigleys.postgresql.org
- https://www.postgresql.org/support/security/CVE-2024-10978/
