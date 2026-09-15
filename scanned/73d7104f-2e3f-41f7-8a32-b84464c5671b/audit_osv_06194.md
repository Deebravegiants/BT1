# [M] Authorization Bypass Through User-Controlled Key in Kibana Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-kibana-2026-63259
Aliases: BIT-elk-2026-63259, CVE-2026-63259
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-kibana-2026-63259
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.4.0 <9.4.4

## Details
Authorization Bypass Through User-Controlled Key (CWE-639) in Kibana can lead to information disclosure via user-supplied identifiers that reference scheduled query result data from Kibana Spaces the requester is not authorized to access.

## References
- https://discuss.elastic.co/t/kibana-9-4-4-security-update-esa-2026-70/388573
- https://nvd.nist.gov/vuln/detail/CVE-2026-63259
