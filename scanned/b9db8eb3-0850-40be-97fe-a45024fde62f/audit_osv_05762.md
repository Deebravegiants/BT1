# [H] OpenFeature evaluation API reads input data with no bounds

## Summary
Severity: High
Advisory: BIT-grafana-2026-27880
Aliases: CVE-2026-27880
Ecosystem: Bitnami
Published: 2026-04-01
Source: https://osv.dev/vulnerability/BIT-grafana-2026-27880
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.4.0 <12.4.2

## Details
The OpenFeature feature toggle evaluation endpoint reads unbounded values into memory, which can cause out-of-memory crashes.

## References
- https://grafana.com/security/security-advisories/cve-2026-27880
- https://nvd.nist.gov/vuln/detail/CVE-2026-27880
- https://access.redhat.com/security/cve/CVE-2026-27880
- https://bugzilla.redhat.com/show_bug.cgi?id=2452295
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27880.json
