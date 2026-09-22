# [M] Kibana Denial of Service issue

## Summary
Severity: Medium
Advisory: BIT-elk-2024-37281
Aliases: BIT-kibana-2024-37281, CVE-2024-37281
Ecosystem: Bitnami
Published: 2024-08-01
Source: https://osv.dev/vulnerability/BIT-elk-2024-37281
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.0.0 <8.14.0

## Details
An issue was discovered in Kibana where a user with Viewer role could cause a Kibana instance to crash by sending a large number of maliciously crafted requests to a specific endpoint.

## References
- https://discuss.elastic.co/t/kibana-7-17-23-8-14-0-security-update-esa-2024-16/364094
- https://nvd.nist.gov/vuln/detail/CVE-2024-37281
