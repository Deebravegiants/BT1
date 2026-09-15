# [M] Envoy vulnerable to bypass of RBAC uri_template permission

## Summary
Severity: Medium
Advisory: BIT-envoy-2025-46821
Aliases: CVE-2025-46821, GHSA-c7cm-838g-6g67
Ecosystem: Bitnami
Published: 2025-05-09
Source: https://osv.dev/vulnerability/BIT-envoy-2025-46821
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.34.0 <1.34.1

## Details
Envoy is a cloud-native edge/middle/service proxy. Prior to versions 1.34.1, 1.33.3, 1.32.6, and 1.31.8, Envoy's URI template matcher incorrectly excludes the `*` character from a set of valid characters in the URI path. As a result URI path containing the `*` character will not match a URI template expressions. This can result in bypass of RBAC rules when configured using the `uri_template` permissions. This vulnerability is fixed in Envoy versions v1.34.1, v1.33.3, v1.32.6, v1.31.8. As a workaround, configure additional RBAC permissions using `url_path` with `safe_regex` expression.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-c7cm-838g-6g67
- https://nvd.nist.gov/vuln/detail/CVE-2025-46821
