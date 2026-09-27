# [C] Incorrect configuration handling allows TLS session re-use without re-validation in Envoy

## Summary
Severity: Critical
Advisory: BIT-envoy-2022-21654
Aliases: CVE-2022-21654, GHSA-5j4x-g36v-m283
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-21654
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.21.0 <1.21.1

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. Envoy's tls allows re-use when some cert validation settings have changed from their default configuration. The only workaround for this issue is to ensure that default tls settings are used. Users are advised to upgrade.

## References
- https://github.com/envoyproxy/envoy/commit/e9f936d85dc1edc34fabd0a1725ec180f2316353
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-5j4x-g36v-m283
- https://nvd.nist.gov/vuln/detail/CVE-2022-21654
