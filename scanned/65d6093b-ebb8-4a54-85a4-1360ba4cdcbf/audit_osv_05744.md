# [M] Grafana alerting wrong permission on datasource rule write endpoint

## Summary
Severity: Medium
Advisory: BIT-grafana-2024-8118
Aliases: CVE-2024-8118
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-grafana-2024-8118
Type: osv

## Affected
- Bitnami: `grafana` — affected >=11.0.0 <11.2.1

## Details
In Grafana, the wrong permission is applied to the alert rule write API endpoint, allowing users with permission to write external alert instances to also write alert rules.

## References
- https://grafana.com/security/security-advisories/cve-2024-8118/
- https://nvd.nist.gov/vuln/detail/CVE-2024-8118
