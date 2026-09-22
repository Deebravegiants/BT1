# [H] Reachable assertion in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2022-29228
Aliases: CVE-2022-29228, GHSA-rww6-8h7g-8jf6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-29228
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.22.1

## Details
Envoy is a cloud-native high-performance proxy. In versions prior to 1.22.1 the OAuth filter would try to invoke the remaining filters in the chain after emitting a local response, which triggers an ASSERT() in newer versions and corrupts memory on earlier versions. continueDecoding() shouldn’t ever be called from filters after a local reply has been sent. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/envoyproxy/envoy/commit/7ffda4e809dec74449ebc330cebb9d2f4ab61360
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rww6-8h7g-8jf6
- https://nvd.nist.gov/vuln/detail/CVE-2022-29228
