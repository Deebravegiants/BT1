# [M] Path traversal in the Tempo and Loki data source plugins

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-10601
Aliases: CVE-2026-10601
Ecosystem: Bitnami
Published: 2026-06-26
Source: https://osv.dev/vulnerability/BIT-grafana-2026-10601
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.2

## Details
A user with Viewer permissions can use specially crafted requests to the Tempo and Loki data source plugins to reach unintended backend endpoints. Depending on the backend configuration this can expose data source credentials, leak internal responses, or trigger administrative actions on the configured backend.

## References
- https://grafana.com/security/security-advisories/cve-2026-10601
- https://nvd.nist.gov/vuln/detail/CVE-2026-10601
