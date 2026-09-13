# [M] Missing Authorization in Kibana Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-elk-2026-63262
Aliases: BIT-kibana-2026-63262, CVE-2026-63262
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-63262
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.4

## Details
Missing Authorization (CWE-862) in Kibana can lead to unauthorized cross-space information disclosure via user-supplied input that circumvents space-level access control.

## References
- https://discuss.elastic.co/t/kibana-9-4-4-security-update-esa-2026-73/388576
- https://nvd.nist.gov/vuln/detail/CVE-2026-63262
