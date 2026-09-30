# [H] X.509 subjectAltName matching bypass in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2022-21656
Aliases: CVE-2022-21656, GHSA-c9g7-xwcv-pjx2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-21656
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.20.2

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. The default_validator.cc implementation used to implement the default certificate validation routines has a "type confusion" bug when processing subjectAltNames. This processing allows, for example, an rfc822Name or uniformResourceIndicator to be authenticated as a domain name. This confusion allows for the bypassing of nameConstraints, as processed by the underlying OpenSSL/BoringSSL implementation, exposing the possibility of impersonation of arbitrary servers. As a result Envoy will trust upstream certificates that should not be trusted.

## References
- https://github.com/envoyproxy/envoy/commit/bb95af848c939cfe5b5ee33c5b1770558077e64e
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-c9g7-xwcv-pjx2
- https://nvd.nist.gov/vuln/detail/CVE-2022-21656
