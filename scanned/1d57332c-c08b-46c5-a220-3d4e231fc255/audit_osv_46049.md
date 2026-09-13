# [H] JLSEC-2026-606

## Summary
Severity: High
Advisory: JLSEC-2026-606
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-606
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Uncontrolled recursion in PostgreSQL SSL and GSS negotiation allows an attacker able to connect to a PostgreSQL `AF_UNIX` socket to achieve sustained denial of service.  If SSL and GSS are both disabled, an attacker can do the same via access to a PostgreSQL TCP socket.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6479/
