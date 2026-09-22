# [M] JLSEC-2026-53

## Summary
Severity: Medium
Advisory: JLSEC-2026-53
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-53
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=14.1.0+0 <16.13.0+0

## Details
Improper validation of type "oidvector" in PostgreSQL allows a database user to disclose a few bytes of server memory.  We have not ruled out viability of attacks that arrange for presence of confidential information in disclosed bytes, but they seem unlikely.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-2003/
