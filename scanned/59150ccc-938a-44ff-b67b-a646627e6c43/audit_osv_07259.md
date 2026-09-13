# [H] Untrusted search path in auth_query connection in PgBouncer

## Summary
Severity: High
Advisory: BIT-pgbouncer-2025-12819
Aliases: CVE-2025-12819
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2025-12819
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.25.1

## Details
Untrusted search path in auth_query connection handler in PgBouncer before 1.25.1 allows an unauthenticated attacker to execute arbitrary SQL during authentication via a malicious search_path parameter in the StartupMessage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12819
- https://www.pgbouncer.org/changelog.html#pgbouncer-125x
- https://lists.debian.org/debian-lts-announce/2025/12/msg00033.html
