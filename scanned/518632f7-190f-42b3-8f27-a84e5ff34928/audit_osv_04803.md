# [H] HTTP/1.1 multiple issues with envoy.reloadable_features.http1_balsa_delay_reset in envoy

## Summary
Severity: High
Advisory: BIT-envoy-2024-53271
Aliases: CVE-2024-53271, GHSA-rmm5-h2wv-mg4f
Ecosystem: Bitnami
Published: 2024-12-20
Source: https://osv.dev/vulnerability/BIT-envoy-2024-53271
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.32.0 <1.32.3

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. In affected versions envoy  does not properly handle http 1.1 non-101 1xx responses. This can lead to downstream failures in networked devices. This issue has been addressed in versions 1.31.5 and 1.32.3. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/envoyproxy/envoy/commit/da56f6da63079baecef9183436ee5f4141a59af8
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rmm5-h2wv-mg4f
- https://nvd.nist.gov/vuln/detail/CVE-2024-53271
