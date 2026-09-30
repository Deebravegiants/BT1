# [M] Envoy OOM vector from HTTP async client with unbounded response buffer for mirror response

## Summary
Severity: Medium
Advisory: BIT-envoy-2024-34364
Aliases: CVE-2024-34364, GHSA-xcj3-h7vf-fw26
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-34364
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. Envoy exposed an out-of-memory (OOM) vector from the mirror response, since async HTTP client will buffer the response with an unbounded buffer.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-xcj3-h7vf-fw26
- https://nvd.nist.gov/vuln/detail/CVE-2024-34364
