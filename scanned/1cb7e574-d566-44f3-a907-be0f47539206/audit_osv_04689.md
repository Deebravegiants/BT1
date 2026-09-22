# [H] Kibana exposure of sensitive information to an unauthorized actor

## Summary
Severity: High
Advisory: BIT-elk-2024-43707
Aliases: BIT-kibana-2024-43707, CVE-2024-43707
Ecosystem: Bitnami
Published: 2025-01-27
Source: https://osv.dev/vulnerability/BIT-elk-2024-43707
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.0.0 <8.15.0

## Details
An issue was identified in Kibana where a user without access to Fleet can view Elastic Agent policies that could contain sensitive information. The nature of the sensitive information depends on the integrations enabled for the Elastic Agent and their respective versions.

## References
- https://discuss.elastic.co/t/kibana-8-15-0-security-update-esa-2024-29-esa-2024-30/373521
- https://nvd.nist.gov/vuln/detail/CVE-2024-43707
