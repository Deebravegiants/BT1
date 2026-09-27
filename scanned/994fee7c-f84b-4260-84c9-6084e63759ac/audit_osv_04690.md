# [M] BIT-elk-2024-43708

## Summary
Severity: Medium
Advisory: BIT-elk-2024-43708
Aliases: BIT-kibana-2024-43708, CVE-2024-43708
Ecosystem: Bitnami
Published: 2025-01-27
Source: https://osv.dev/vulnerability/BIT-elk-2024-43708
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.0.0 <8.15.0

## Details
An allocation of resources without limits or throttling in Kibana can lead to a crash caused by a specially crafted payload to a number of inputs in Kibana UI. This can be carried out by users with read access to any feature in Kibana.

## References
- https://discuss.elastic.co/t/kibana-7-17-23-8-15-0-security-updates-esa-2024-32-esa-2024-33/373548
- https://nvd.nist.gov/vuln/detail/CVE-2024-43708
