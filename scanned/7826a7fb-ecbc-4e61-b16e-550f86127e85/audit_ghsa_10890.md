# [H] Parse Server affected by denial-of-service via unbounded query complexity in REST and GraphQL API

## Summary
Severity: High
Advisory: GHSA-cmj3-wx7h-ffvg
CVE: CVE-2026-30946
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-cmj3-wx7h-ffvg
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.15
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.2

## Details
### Impact

An unauthenticated attacker can exhaust Parse Server resources (CPU, memory, database connections) through crafted queries that exploit the lack of complexity limits in the REST and GraphQL APIs.

All Parse Server deployments using the REST or GraphQL API are affected.

### Patches

The vulnerability is fixed by introducing configurable request complexity limits via the `requestComplexity` server option with the following keys:

- `subqueryDepth`: Maximum nesting depth for `$inQuery`, `$notInQuery`, `$select`, `$dontSelect`
- `includeDepth`: Maximum depth of dot-separated `include` paths
- `includeCount`: Maximum number of `include` fields per query
- `graphQLDepth`: Maximum depth of GraphQL field selections
- `graphQLFields`: Maximum number of field selections in a GraphQL query

Requests using master key or maintenance key bypass these limits. Set any property to `-1` to disable that specific limit.

In versions `8.6.15` and `9.5.2-alpha.2`, these limits were enabled by default. This unintentionally introduced a breaking change for some applications with legitimate complex queries. In versions `8.6.46` and `9.6.0-alpha.22`, the defaults were changed to `-1` (disabled) to restore backwards compatibility.

The limits remain available as configuration options. To mitigate the vulnerability, upgrade to a patched version and set each `requestComplexity` property to a value appropriate for your application.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-cmj3-wx7h-ffvg
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.2
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.15

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-cmj3-wx7h-ffvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-30946
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.15
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.2
