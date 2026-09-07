# [M] @keystone-6/core: `isFilterable` bypass via `cursor` parameter in findMany (CVE-2025-46720 incomplete fix)

## Summary
Severity: Medium
Advisory: GHSA-cgcg-q9jh-5pr2
CVE: CVE-2026-33326
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-cgcg-q9jh-5pr2
Type: github-advisory

## Affected
- npm: `@keystone-6/core` — affected >=0 <6.5.2

## Details
# Summary  
`{field}.isFilterable` access control can be bypassed in `findMany` queries by passing a `cursor`.  This can be used to confirm the existence of records by protected field values.

The fix for [CVE-2025-46720](https://github.com/keystonejs/keystone/security/advisories/GHSA-hg9m-67mm-7pg3) (field-level `isFilterable` bypass for update and delete mutations) added checks to the `where` parameter in `update` and `delete` mutations however the `cursor` parameter in `findMany` was not patched and accepts the same `UniqueWhere` input type.

# Impact  
This affects any project relying on `isFilterable` behaviour (at the list or field level) to prevent external users from using the filtering of fields as a discovery mechanism. `isFilterable` access control using a function can be bypassed by using the `cursor` input.

This has no impact on projects using `isFilterable: false` or `defaultIsFilterable: false` for sensitive fields, or if you have otherwise omitted filtering by these fields from your GraphQL schema. (See workarounds)

# Patches  
This issue has been patched in `@keystone-6/core` version 6.5.2.

# Workarounds  
To mitigate this issue in older versions where patching is not a viable pathway.

- Set `{field}.isFilterable: false` statically for relevant fields to prevent filtering by them earlier in the access control pipeline (that is, don't use functions)
- Set `{field}.graphql.omit.read: true` for relevant fields, which implicitly removes filtering by these fields your GraphQL schema

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-cgcg-q9jh-5pr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33326
- https://github.com/keystonejs/keystone
