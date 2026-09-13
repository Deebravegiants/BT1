# [H] Happy Eyeballs: Validate that additional_address are IP addresses instead of crashing when sorting in envoy

## Summary
Severity: High
Advisory: BIT-envoy-2024-53269
Aliases: CVE-2024-53269, GHSA-mfqp-7mmj-rm53
Ecosystem: Bitnami
Published: 2024-12-20
Source: https://osv.dev/vulnerability/BIT-envoy-2024-53269
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.32.0 <1.32.2

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. When additional address are not ip addresses, then the Happy Eyeballs sorting algorithm will crash in data plane. This issue has been addressed in releases 1.32.2, 1.31.4, and 1.30.8. Users are advised to upgrade. Users unable to upgrade may disable Happy Eyeballs and/or change the IP configuration.

## References
- https://github.com/envoyproxy/envoy/pull/37743/commits/3f62168d86aceb90f743f63b50cc711710b1c401
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-mfqp-7mmj-rm53
- https://nvd.nist.gov/vuln/detail/CVE-2024-53269
