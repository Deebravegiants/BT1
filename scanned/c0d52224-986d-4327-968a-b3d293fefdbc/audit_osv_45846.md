# [H] JLSEC-2026-40

## Summary
Severity: High
Advisory: JLSEC-2026-40
Ecosystem: Julia
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-40
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.0.0+0

## Details
`schema_element` defeats protective `search_path` changes; It was found that certain database calls in PostgreSQL could permit an authed attacker with elevated database-level privileges to execute arbitrary code.

## References
- https://access.redhat.com/security/cve/CVE-2023-2454
- https://security.netapp.com/advisory/ntap-20230706-0006/
- https://www.postgresql.org/support/security/CVE-2023-2454/
