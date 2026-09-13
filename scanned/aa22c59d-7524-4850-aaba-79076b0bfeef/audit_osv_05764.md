# [M] Grafana Live push endpoint allows unbounded memory allocation leading to OOM

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-28376
Aliases: CVE-2026-28376
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-28376
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
The Grafana Live push endpoint can be exploited to cause unbounded memory allocation by sending a large or streaming request body, potentially leading to out-of-memory conditions. An authenticated user with access to the Grafana Live API can trigger this issue.

## References
- https://grafana.com/security/security-advisories/cve-2026-28376
- https://nvd.nist.gov/vuln/detail/CVE-2026-28376
