# [M] Kibana server-side request forgery

## Summary
Severity: Medium
Advisory: BIT-elk-2024-43710
Aliases: BIT-kibana-2024-43710, CVE-2024-43710
Ecosystem: Bitnami
Published: 2025-01-27
Source: https://osv.dev/vulnerability/BIT-elk-2024-43710
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.7.0 <8.15.0

## Details
A server side request forgery vulnerability was identified in Kibana where the /api/fleet/health_check API could be used to send requests to internal endpoints. Due to the nature of the underlying request, only endpoints available over https that return JSON could be accessed. This can be carried out by users with read access to Fleet.

## References
- https://discuss.elastic.co/t/kibana-8-15-0-security-update-esa-2024-29-esa-2024-30/373521
- https://nvd.nist.gov/vuln/detail/CVE-2024-43710
