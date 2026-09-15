# [M] Envoy: PROXY Protocol v2 header generator emits "skipped" TLVs, causing 65 KB attacker-controlled spillover into the upstream application stream

## Summary
Severity: Medium
Advisory: BIT-envoy-2026-47692
Aliases: CVE-2026-47692, GHSA-wh36-hm39-mm3r
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47692
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.34.0 until 1.35.13, 1.36.9, 1.37.5, and 1.38.3, PROXY Protocol v2 header generator emits TLVs beyond the maximum length of 65535 bytes, causing a mismatch between bytes written and the length field in the header. This can result in smuggled bytes on the upstream request. This vulnerability is fixed in 1.35.13, 1.36.9, 1.37.5, and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-wh36-hm39-mm3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-47692
