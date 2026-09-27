# [M] JLSEC-2026-602

## Summary
Severity: Medium
Advisory: JLSEC-2026-602
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-602
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Externally-controlled format string in PostgreSQL timeofday() function allows an attacker to retrieve portions of server memory, via crafted timezone zones.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6474/
