# [C] ProxySQL pre-auth heap overflow in MySQL and PostgreSQL first-packet handling

## Summary
Severity: Critical
Advisory: BIT-proxysql-2026-48773
Aliases: CVE-2026-48773, GHSA-58ww-865x-grpr
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-proxysql-2026-48773
Type: osv

## Affected
- Bitnami: `proxysql` — affected >=2.0.18 <3.0.9

## Details
ProxySQL is a proxy for MySQL and its forks, as well as PostgreSQL. Versions 2.0.18 through 3.0.8 have a pre-authentication heap memory corruption vulnerability in the MySQL and PostgreSQL protocol first-read paths. A remote unauthenticated client can declare an oversized first packet length, and ProxySQL passes that attacker-controlled length directly to `recv()` while writing into a fixed 32 KB input queue. Version 3.0.9 patches the issue.

## References
- https://github.com/sysown/proxysql/releases/tag/v3.0.9
- https://github.com/sysown/proxysql/security/advisories/GHSA-58ww-865x-grpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48773
