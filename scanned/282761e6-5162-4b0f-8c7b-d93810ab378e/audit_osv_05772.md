# [H] Pre-authentication denial of service in the public dashboard query endpoint

## Summary
Severity: High
Advisory: BIT-grafana-2026-42127
Aliases: CVE-2026-42127
Ecosystem: Bitnami
Published: 2026-06-26
Source: https://osv.dev/vulnerability/BIT-grafana-2026-42127
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.2

## Details
The public dashboard query endpoint does not limit request body size before processing, allowing unauthenticated attackers to trigger excessive memory allocation by sending arbitrarily large JSON payloads. This can lead to denial of service through memory exhaustion. No valid dashboard access token or authentication is required to exploit this vulnerability.

## References
- https://grafana.com/security/security-advisories/cve-2026-42127
- https://nvd.nist.gov/vuln/detail/CVE-2026-42127
