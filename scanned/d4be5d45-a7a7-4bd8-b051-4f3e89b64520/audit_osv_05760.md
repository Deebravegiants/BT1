# [M] CVE-2026-21723 Record

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-21723
Aliases: CVE-2026-21723
Ecosystem: Bitnami
Published: 2026-07-29
Source: https://osv.dev/vulnerability/BIT-grafana-2026-21723
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.3.0 <12.3.3

## Details
The alertmanager templates test endpoint (/api/alertmanager/grafana/config/api/v1/templates/test) can execute templates with no memory limits. Mass-executing templates in a short period causes OOM and crashes the Grafana service. The endpoint requires very low privileges and is exploitable with anonymous access enabled.

## References
- https://grafana.com/security/security-advisories/cve-2026-21723
- https://nvd.nist.gov/vuln/detail/CVE-2026-21723
