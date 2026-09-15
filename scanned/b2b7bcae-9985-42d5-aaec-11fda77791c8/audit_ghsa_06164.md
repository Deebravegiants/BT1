# [H] Keystone vulnerable to `graphql.maxTake` bypass with negative `take`

## Summary
Severity: High
Advisory: GHSA-cqmq-8755-7xvh
CVE: CVE-2026-63421
CWE: CWE-20, CWE-480
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-cqmq-8755-7xvh
Type: github-advisory

## Affected
- npm: `@keystone-6/core` — affected >=0 <6.5.3

## Details
# Summary
The value of `graphql.maxTake` can be bypassed by providing a negative input.
This can be used to exceed the developer's intended `graphql.maxTake` value, allowing queries to return results in excess of the `graphql.maxTake` value set.

# Impact
This affects any project relying on `graphql.maxTake` to bound the number of items returned per query.

# Patches
This issue has been patched in `@keystone-6/core` version `6.5.3`.

If you cannot patch, you can workaround this by restricting `take` input values in your GraphQL queries to the bounded value, or by blocking negative values.

# Credit
This issue was found by [Haxset's](https://haxset.com) Security Scanner and validated by their team.

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-cqmq-8755-7xvh
- https://github.com/keystonejs/keystone/pull/9859
- https://github.com/keystonejs/keystone/commit/9fb88b246950ce4de754a43fe6416f20403577b1
- https://github.com/keystonejs/keystone
- https://github.com/keystonejs/keystone/releases/tag/@keystone-6/core@6.5.3
