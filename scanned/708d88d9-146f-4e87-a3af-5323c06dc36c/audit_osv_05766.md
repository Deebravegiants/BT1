# [M] Grafana plugin resources can lead to unbounded memory allocation

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-28383
Aliases: CVE-2026-28383
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-28383
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
A request to the Grafana plugin resources endpoint can cause unbounded memory allocation by reading the entire request body into memory. An authenticated user can exploit this to trigger an out-of-memory condition, potentially causing a denial of service.

## References
- https://grafana.com/security/security-advisories/cve-2026-28383
- https://nvd.nist.gov/vuln/detail/CVE-2026-28383
