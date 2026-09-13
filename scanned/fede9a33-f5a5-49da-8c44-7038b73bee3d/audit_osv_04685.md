# [M] Kibana Broken Access Control issue

## Summary
Severity: Medium
Advisory: BIT-elk-2024-37279
Aliases: BIT-kibana-2024-37279, CVE-2024-37279
Ecosystem: Bitnami
Published: 2024-06-17
Source: https://osv.dev/vulnerability/BIT-elk-2024-37279
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.6.3 <8.14.0

## Details
A flaw was discovered in Kibana, allowing view-only users of alerting to use the run_soon API making the alerting rule run continuously, potentially affecting the system availability if the alerting rule is running complex queries.

## References
- https://discuss.elastic.co/t/kibana-8-14-0-security-update-esa-2024-15/360887
- https://nvd.nist.gov/vuln/detail/CVE-2024-37279
