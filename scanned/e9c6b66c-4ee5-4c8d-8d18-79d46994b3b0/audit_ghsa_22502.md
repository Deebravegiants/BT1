# [C] EnvoyProxy Envoy Missing HTTP URL path normalization

## Summary
Severity: Critical
Advisory: GHSA-2wmf-p7f8-w42h
CVE: CVE-2019-9901
CWE: CWE-706
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2wmf-p7f8-w42h
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected >=0 <1.9.1

## Details
Envoy 1.9.0 and before does not normalize HTTP URL paths. A remote attacker may craft a relative path, e.g., `something/../admin`, to bypass access control, e.g., a block on `/admin`. A backend server could then interpret the non-normalized path and provide an attacker access beyond the scope provided for by the access control policy.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-xcx5-93pw-jw2w
- https://nvd.nist.gov/vuln/detail/CVE-2019-9901
- https://github.com/envoyproxy/envoy/issues/6435
- https://github.com/envoyproxy/envoy/commit/e668e669677e52a00d99652b5a260d1cedafdfa8
- https://github.com/envoyproxy/envoy
- https://github.com/envoyproxy/envoy/blob/main/security/postmortems/cve-2019-9900.md
- https://groups.google.com/forum/#!topic/envoy-announce/VoHfnDqZiAM
- https://www.envoyproxy.io/docs/envoy/v1.9.1/intro/version_history
