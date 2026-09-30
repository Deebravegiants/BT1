# [C] Trivial authentication bypass in Envoy

## Summary
Severity: Critical
Advisory: BIT-envoy-2022-29226
Aliases: CVE-2022-29226, GHSA-h45c-2f94-prxh
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-29226
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.22.1

## Details
Envoy is a cloud-native high-performance proxy. In versions prior to 1.22.1 the OAuth filter implementation does not include a mechanism for validating access tokens, so by design when the HMAC signed cookie is missing a full authentication flow should be triggered. However, the current implementation assumes that access tokens are always validated thus allowing access in the presence of any access token attached to the request. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/envoyproxy/envoy/commit/7ffda4e809dec74449ebc330cebb9d2f4ab61360
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-h45c-2f94-prxh
- https://nvd.nist.gov/vuln/detail/CVE-2022-29226
