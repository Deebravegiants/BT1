# [H] Denial of service via unbounded request body size

## Summary
Severity: High
Advisory: BIT-grafana-2026-33382
Aliases: CVE-2026-33382
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-grafana-2026-33382
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.2

## Details
Several Grafana API endpoints, some of them unauthenticated, do not limit the size of the request body before processing it. An attacker can send very large payloads that force excessive memory allocation, potentially exhausting memory and causing a denial of service.

## References
- https://grafana.com/security/security-advisories/cve-2026-33382
- https://nvd.nist.gov/vuln/detail/CVE-2026-33382
