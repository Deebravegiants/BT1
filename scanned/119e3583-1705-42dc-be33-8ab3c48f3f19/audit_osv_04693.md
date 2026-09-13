# [M] Kibana privilege escalation via reporting_user role

## Summary
Severity: Medium
Advisory: BIT-elk-2025-25010
Aliases: BIT-kibana-2025-25010, CVE-2025-25010
Ecosystem: Bitnami
Published: 2025-08-30
Source: https://osv.dev/vulnerability/BIT-elk-2025-25010
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.1.0 <9.1.3

## Details
Incorrect authorization in Kibana can lead to privilege escalation via the built-in reporting_user role which incorrectly has the ability to access all Kibana Spaces.

## References
- https://discuss.elastic.co/t/kibana-9-0-6-9-1-3-security-update-esa-2025-13/381426
- https://nvd.nist.gov/vuln/detail/CVE-2025-25010
