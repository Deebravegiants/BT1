# [M] BIT-elk-2024-52974

## Summary
Severity: Medium
Advisory: BIT-elk-2024-52974
Aliases: BIT-kibana-2024-52974, CVE-2024-52974
Ecosystem: Bitnami
Published: 2025-04-10
Source: https://osv.dev/vulnerability/BIT-elk-2024-52974
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.0.0 <8.15.1

## Details
An issue has been identified where a specially crafted request sent to an Observability API could cause the kibana server to crash.

A successful attack requires a malicious user to have read permissions for Observability assigned to them.

## References
- https://discuss.elastic.co/t/kibana-7-17-23-and-8-15-1-security-update-esa-2024-36/376923
- https://nvd.nist.gov/vuln/detail/CVE-2024-52974
