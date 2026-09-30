# [M] GraphQL API endpoint ignores CORS origin restriction

## Summary
Severity: Medium
Advisory: GHSA-q3p6-g7c4-829c
CVE: CVE-2026-34373
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-q3p6-g7c4-829c
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.10
- npm: `parse-server` — affected >=3.5.0 <8.6.66

## Details
### Impact

The GraphQL API endpoint does not respect the `allowOrigin` server option and unconditionally allows cross-origin requests from any website. This bypasses origin restrictions that operators configure to control which websites can interact with the Parse Server API. The REST API correctly enforces the configured `allowOrigin` restriction.

### Patches

The GraphQL API endpoint now uses the same CORS middleware as the REST API, ensuring the `allowOrigin` and `allowHeaders` server options are consistently enforced across all endpoints.

### Workarounds

There is no known workaround other than upgrading.

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-q3p6-g7c4-829c
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10334
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10335

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-q3p6-g7c4-829c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34373
- https://github.com/parse-community/parse-server/pull/10334
- https://github.com/parse-community/parse-server/pull/10335
- https://github.com/parse-community/parse-server/commit/0347641507891d0013ec57f7c10f012064f41263
- https://github.com/parse-community/parse-server/commit/4dd0d3d8be1c39664c74ad10bb0abaa76bc41203
- https://github.com/parse-community/parse-server
