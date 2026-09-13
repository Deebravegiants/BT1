# [M] Parse Server: GraphQL `__type` introspection bypass via inline fragments when public introspection is disabled

## Summary
Severity: Medium
Advisory: GHSA-q5q9-2rhp-33qw
CVE: CVE-2026-30854
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-q5q9-2rhp-33qw
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.3.1-alpha.3 <9.5.0-alpha.10

## Details
### Impact

When `graphQLPublicIntrospection` is disabled, `__type` queries nested inside inline fragments (e.g. `... on Query { __type(name:"User") { name } })` bypass the introspection control, allowing unauthenticated users to perform type reconnaissance. `__schema` introspection is not affected.

### Patches

The check was changed from a flat iteration over root-level selections to a recursive walk of all selection sets, detecting `__type` inside inline fragments at any depth.

### Workarounds

Require master key authentication at the network layer (e.g. reverse proxy) for the GraphQL endpoint.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-q5q9-2rhp-33qw
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.10

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-q5q9-2rhp-33qw
- https://nvd.nist.gov/vuln/detail/CVE-2026-30854
- https://github.com/parse-community/parse-server
