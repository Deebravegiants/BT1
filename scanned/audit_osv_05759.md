# [M] Public Dashboards time range restriction on annotations can be bypassed

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-21722
Aliases: CVE-2026-21722
Ecosystem: Bitnami
Published: 2026-02-20
Source: https://osv.dev/vulnerability/BIT-grafana-2026-21722
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.3.0 <12.3.2

## Details
Public dashboards with annotations enabled did not limit their annotation timerange to the locked timerange of the public dashboard. This means one could read the entire history of annotations visible on the specific dashboard, even those outside the locked timerange.

This did not leak any annotations that would not otherwise be visible on the public dashboard.

## References
- https://grafana.com/security/security-advisories/CVE-2026-21722
- https://nvd.nist.gov/vuln/detail/CVE-2026-21722
- https://grafana.com/security/security-advisories/cve-2026-21722
