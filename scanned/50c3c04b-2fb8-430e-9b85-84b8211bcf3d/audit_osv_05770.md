# [M] Grafana Data Source Plugin: DoS (OOM) via Negative Interval Injection in $__timeGroup Macro

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-33378
Aliases: CVE-2026-33378
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-33378
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
Using the $__timeGroup macro, one can achieve an OOM by overloading the server. This requires a SQL datasource. If the server is set up to auto-restart, the impact is minimal or non-existent, as the attack can take upwards of half an hour to crash the server.

## References
- https://grafana.com/security/security-advisories/cve-2026-33378
- https://nvd.nist.gov/vuln/detail/CVE-2026-33378
