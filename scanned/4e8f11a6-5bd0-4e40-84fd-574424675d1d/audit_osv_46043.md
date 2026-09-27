# [M] JLSEC-2026-600

## Summary
Severity: Medium
Advisory: JLSEC-2026-600
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-600
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Missing authorization in PostgreSQL CREATE TYPE allows an object creator to hijack other queries that use `search_path` to find user-defined types, including extension-defined types.  That is to say, the victim will execute arbitrary SQL functions of the attacker's choice.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6472/
