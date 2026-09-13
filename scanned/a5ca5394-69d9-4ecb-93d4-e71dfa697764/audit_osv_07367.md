# [H] PostgreSQL SSL/GSS init causes denial of service, via uncontrolled recursion

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6479
Aliases: CVE-2026-6479
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6479
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Uncontrolled recursion in PostgreSQL SSL and GSS negotiation allows an attacker able to connect to a PostgreSQL AF_UNIX socket to achieve sustained denial of service.  If SSL and GSS are both disabled, an attacker can do the same via access to a PostgreSQL TCP socket.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6479
- https://www.postgresql.org/support/security/CVE-2026-6479/
