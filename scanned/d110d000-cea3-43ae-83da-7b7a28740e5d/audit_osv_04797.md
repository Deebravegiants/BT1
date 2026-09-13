# [H] oghttp2 crash on OnBeginHeadersForStream in envoy

## Summary
Severity: High
Advisory: BIT-envoy-2024-45807
Aliases: CVE-2024-45807, GHSA-qc52-r4x5-9w37
Ecosystem: Bitnami
Published: 2024-09-21
Source: https://osv.dev/vulnerability/BIT-envoy-2024-45807
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.31.0 <1.31.2

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. Envoy's 1.31 is using `oghttp` as the default HTTP/2 codec, and there are potential bugs around stream management in the codec. To resolve this Envoy will switch off the `oghttp2` by default. The impact of this issue is that envoy will crash. This issue has been addressed in release version 1.31.2. All users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-qc52-r4x5-9w37
- https://nvd.nist.gov/vuln/detail/CVE-2024-45807
