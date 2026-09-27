# [M] Viewer-triggered race condition in Grafana Live leads to complete server crash

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-28379
Aliases: CVE-2026-28379
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-28379
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
A race condition in Grafana Live allows authenticated users with Viewer role to trigger a server crash by sending concurrent requests that cause a fatal map access error. This results in complete service unavailability requiring restart of the Grafana server.

## References
- https://grafana.com/security/security-advisories/cve-2026-28379
- https://nvd.nist.gov/vuln/detail/CVE-2026-28379
