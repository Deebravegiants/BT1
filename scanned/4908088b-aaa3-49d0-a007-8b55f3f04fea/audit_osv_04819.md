# [H] Envoy: Stack overflow in destructor of highly nested JSON

## Summary
Severity: High
Advisory: BIT-envoy-2026-48042
Aliases: CVE-2026-48042, GHSA-f24p-rxw2-g6pv
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-48042
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.1

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to 1.35.11, 1.36.7, 1.37.3, and 1.38.1, destructor of JSON Object results in stack overflow when deeply O(100K) nested objects are present. This vulnerability is fixed in 1.35.11, 1.36.7, 1.37.3, and 1.38.1.

## References
- https://github.com/envoyproxy/envoy/blob/099a9d71ebfd8aa9f823e1738b34138cb634a07b/source/common/json/json_loader.h#L21
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-f24p-rxw2-g6pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48042
