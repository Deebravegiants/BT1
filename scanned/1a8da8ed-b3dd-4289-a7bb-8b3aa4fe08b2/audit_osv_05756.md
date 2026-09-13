# [M] SQL Data Source Plugin: OOM DoS via $__timeGroup macro

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-19475
Aliases: CVE-2026-19475
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-grafana-2026-19475
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.1.0 <13.1.5

## Details
An authenticated user with permission to query a SQL data source can bypass the fix for CVE-2026-33375 by injecting the timeGroup macro through a WHERE clause, which Grafana's regex-based macro parsing does not reject. Evaluating the injected macro causes uncontrolled memory consumption that can terminate the Grafana server process, resulting in a denial of service. The Microsoft SQL Server, PostgreSQL, and MySQL data sources are affected.

## References
- https://grafana.com/security/security-advisories/cve-2026-19475
- https://nvd.nist.gov/vuln/detail/CVE-2026-19475
