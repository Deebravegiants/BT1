# [M] Envoy Gateway custom backendRef cross-namespace ReferenceGrant bypass

## Summary
Severity: Medium
Advisory: GHSA-fcrp-7gc2-93g7
CVE: CVE-2026-53718
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-fcrp-7gc2-93g7
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
### Impact
Envoy Gateway accepts extension-managed custom backendRefs from an HTTPRoute to a backend resource in another namespace without requiring a matching Gateway API ReferenceGrant in the target namespace. This breaks the Gateway API cross-namespace consent model: the namespace that owns the referenced backend resource does not need to opt in with a ReferenceGrant before another namespace’s HTTPRoute can use that resource.

### Patches
[1.7.4](https://github.com/envoyproxy/gateway/releases/tag/v1.7.4)
[1.8.1](https://github.com/envoyproxy/gateway/releases/tag/v1.8.1)

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-fcrp-7gc2-93g7
- https://github.com/envoyproxy/gateway
