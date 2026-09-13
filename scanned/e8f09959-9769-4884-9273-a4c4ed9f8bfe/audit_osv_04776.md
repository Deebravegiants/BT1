# [C] Envoy vulnerable to OAuth2 credentials exploit with permanent validity

## Summary
Severity: Critical
Advisory: BIT-envoy-2023-35941
Aliases: CVE-2023-35941, GHSA-7mhv-gr67-hq55
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-35941
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.26.0 <1.26.4

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12, a malicious client is able to construct credentials with permanent validity in some specific scenarios. This is caused by the some rare scenarios in which HMAC payload can be always valid in OAuth2 filter's check. Versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12 have a fix for this issue. As a workaround, avoid wildcards/prefix domain wildcards in the host's domain configuration.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-7mhv-gr67-hq55
- https://nvd.nist.gov/vuln/detail/CVE-2023-35941
