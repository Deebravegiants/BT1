# [M] Kibana Unrestricted Upload of File

## Summary
Severity: Medium
Advisory: BIT-kibana-2025-25016
Aliases: BIT-elk-2025-25016, CVE-2025-25016
Ecosystem: Bitnami
Published: 2025-05-03
Source: https://osv.dev/vulnerability/BIT-kibana-2025-25016
Type: osv

## Affected
- Bitnami: `kibana` — affected >=8.0.0 <8.13.0

## Details
Unrestricted file upload in Kibana allows an authenticated attacker to compromise software integrity by uploading a crafted malicious file due to insufficient server-side validation.

## References
- https://discuss.elastic.co/t/kibana-7-17-19-and-8-13-0-security-update-esa-2024-47/377711
- https://nvd.nist.gov/vuln/detail/CVE-2025-25016
