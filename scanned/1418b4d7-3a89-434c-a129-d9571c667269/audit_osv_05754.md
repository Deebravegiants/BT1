# [H] CVE-2026-17183 CVE Record

## Summary
Severity: High
Advisory: BIT-grafana-2026-17183
Aliases: CVE-2026-17183
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-grafana-2026-17183
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.1.0 <13.1.4

## Details
An authenticated user with permission to create or edit alert rules can bypass datasource query authorization by marking an alert rule query as a server-side expression while referencing a real datasource UID (incorrect authorization). This can expose data accessible through Grafana's configured datasource credentials to users who lack permission to query that datasource.

## References
- https://grafana.com/security/security-advisories/cve-2026-17183
- https://nvd.nist.gov/vuln/detail/CVE-2026-17183
