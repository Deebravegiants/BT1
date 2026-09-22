# [M] Malicious log injection via access logs in envoy

## Summary
Severity: Medium
Advisory: BIT-envoy-2024-45808
Aliases: CVE-2024-45808, GHSA-p222-xhp9-39rc
Ecosystem: Bitnami
Published: 2024-09-21
Source: https://osv.dev/vulnerability/BIT-envoy-2024-45808
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.31.0 <1.31.2

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. A vulnerability has been identified in Envoy that allows malicious attackers to inject unexpected content into access logs. This is achieved by exploiting the lack of validation for the `REQUESTED_SERVER_NAME` field for access loggers. This issue has been addressed in versions 1.31.2, 1.30.6, 1.29.9, and 1.28.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-p222-xhp9-39rc
- https://nvd.nist.gov/vuln/detail/CVE-2024-45808
