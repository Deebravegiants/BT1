# [C] Kibana arbitrary code execution via prototype pollution

## Summary
Severity: Critical
Advisory: BIT-elk-2025-25014
Aliases: BIT-kibana-2025-25014, CVE-2025-25014
Ecosystem: Bitnami
Published: 2025-05-08
Source: https://osv.dev/vulnerability/BIT-elk-2025-25014
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.0.1

## Details
A Prototype pollution vulnerability in Kibana leads to arbitrary code execution via crafted HTTP requests to machine learning and reporting endpoints.

## References
- https://discuss.elastic.co/t/kibana-8-17-6-8-18-1-or-9-0-1-security-update-esa-2025-07/377868
- https://nvd.nist.gov/vuln/detail/CVE-2025-25014
