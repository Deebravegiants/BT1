# [H] Envoy affected by a crash in EnvoyQuicServerStream::OnInitialHeadersComplete()

## Summary
Severity: High
Advisory: BIT-envoy-2024-32974
Aliases: CVE-2024-32974, GHSA-mgxp-7hhp-8299
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-32974
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. A crash was observed in `EnvoyQuicServerStream::OnInitialHeadersComplete()` with following call stack. It is a use-after-free caused by QUICHE continuing push request headers after `StopReading()` being called on the stream. As after `StopReading()`, the HCM's `ActiveStream` might have already be destroyed and any up calls from QUICHE could potentially cause use after free.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-mgxp-7hhp-8299
- https://nvd.nist.gov/vuln/detail/CVE-2024-32974
