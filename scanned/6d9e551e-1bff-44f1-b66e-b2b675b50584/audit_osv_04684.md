# [M] BIT-elk-2024-23443

## Summary
Severity: Medium
Advisory: BIT-elk-2024-23443
Aliases: BIT-kibana-2024-23443, CVE-2024-23443
Ecosystem: Bitnami
Published: 2024-06-21
Source: https://osv.dev/vulnerability/BIT-elk-2024-23443
Type: osv

## Affected
- Bitnami: `elk` — affected >=0 <8.14.0

## Details
A high-privileged user, allowed to create custom osquery packs 17 could affect the availability of Kibana by uploading a maliciously crafted osquery pack.

## References
- https://discuss.elastic.co/t/kibana-8-14-0-7-17-22-security-update-esa-2024-11/361460
- https://nvd.nist.gov/vuln/detail/CVE-2024-23443
