# [H] Pre-authentication denial of service via the OAuth login route

## Summary
Severity: High
Advisory: BIT-grafana-2026-8609
Aliases: CVE-2026-8609
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-grafana-2026-8609
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.2

## Details
An unauthenticated attacker can repeatedly call Grafana's OAuth login route with unique values, causing unbounded memory growth that can eventually exhaust memory and crash the Grafana instance (denial of service).

## References
- https://grafana.com/security/security-advisories/cve-2026-8609
- https://nvd.nist.gov/vuln/detail/CVE-2026-8609
