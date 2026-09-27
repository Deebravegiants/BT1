# [H] PostgreSQL pg_trgm heap buffer overflow writes pattern onto server memory

## Summary
Severity: High
Advisory: BIT-postgresql-2026-2007
Aliases: CVE-2026-2007
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-2007
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.2.0

## Details
Heap buffer overflow in PostgreSQL pg_trgm allows a database user to achieve unknown impacts via a crafted input string.  The attacker has limited control over the byte patterns to be written, but we have not ruled out the viability of attacks that lead to privilege escalation.  PostgreSQL 18.1 and 18.0 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2007
- https://www.postgresql.org/support/security/CVE-2026-2007/
- https://access.redhat.com/errata/RHSA-2026:19009
- https://access.redhat.com/errata/RHSA-2026:8756
- https://access.redhat.com/security/cve/CVE-2026-2007
- https://bugzilla.redhat.com/show_bug.cgi?id=2439320
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2007.json
