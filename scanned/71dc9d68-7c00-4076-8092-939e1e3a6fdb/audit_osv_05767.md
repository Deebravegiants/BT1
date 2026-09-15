# [M] Grafana MSSQL Data Source Plugin: Restriction Bypass Leading to OOM DoS

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-33375
Aliases: CVE-2026-33375
Ecosystem: Bitnami
Published: 2026-04-01
Source: https://osv.dev/vulnerability/BIT-grafana-2026-33375
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.4.0 <12.4.2

## Details
The Grafana MSSQL data source plugin contains a logic flaw that allows a low-privileged user (Viewer) to bypass API restrictions and trigger a catastrophic Out-Of-Memory (OOM) memory exhaustion, crashing the host container.

## References
- https://grafana.com/security/security-advisories/cve-2026-33375
- https://nvd.nist.gov/vuln/detail/CVE-2026-33375
