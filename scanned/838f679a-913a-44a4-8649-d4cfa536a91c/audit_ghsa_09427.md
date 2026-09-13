# [M] Parse Server's GraphQL "Did you mean ...?" validation suggestions disclose schema to unauthenticated callers

## Summary
Severity: Medium
Advisory: GHSA-8cph-rgr4-g5vj
CVE: CVE-2026-47248
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-8cph-rgr4-g5vj
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.9.1-alpha.2
- npm: `parse-server` — affected >=0 <8.6.78

## Details
### Impact

Parse Server's GraphQL endpoint discloses schema metadata to unauthenticated callers through `Did you mean ...?` suggestions embedded in GraphQL validation-error messages. An unauthenticated caller who knows only the public application id can iteratively send malformed queries to reconstruct class names, field names, argument names, mutation names, and input-object fields. This bypasses the `IntrospectionControlPlugin` enforced when `graphQLPublicIntrospection: false` (the default) and defeats the schema-hiding goal of prior advisories GHSA-48q3-prgv-gm4w and GHSA-q5q9-2rhp-33qw. Schema disclosure aids reconnaissance for downstream authorization probing but does not by itself leak object data or authentication material.

### Patches

A new `SchemaSuggestionsControlPlugin` Apollo plugin strips the `Did you mean ...?` suffix from GraphQL validation-error messages during `validationDidStart`, which runs before any introspection gate. The plugin applies only when `graphQLPublicIntrospection: false` and the caller is not a master-key or maintenance-key holder, matching the trust model of the existing `IntrospectionControlPlugin`.

### Workarounds

No code workaround is available short of disabling the GraphQL API (`mountGraphQL: false`). Operators who require disclosure-resistant validation errors should upgrade to a patched release.

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-8cph-rgr4-g5vj
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10467
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10468

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-8cph-rgr4-g5vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47248
- https://github.com/parse-community/parse-server/pull/10467
- https://github.com/parse-community/parse-server/pull/10468
- https://github.com/parse-community/parse-server
