# [H] Envoy can crash due to uncaught nlohmann JSON exception

## Summary
Severity: High
Advisory: BIT-envoy-2024-34363
Aliases: CVE-2024-34363, GHSA-g979-ph9j-5gg4
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-34363
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. Due to how Envoy invoked the nlohmann JSON library, the library could throw an uncaught exception from downstream data if incomplete UTF-8 strings were serialized. The uncaught exception would cause Envoy to crash.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-g979-ph9j-5gg4
- https://nvd.nist.gov/vuln/detail/CVE-2024-34363
