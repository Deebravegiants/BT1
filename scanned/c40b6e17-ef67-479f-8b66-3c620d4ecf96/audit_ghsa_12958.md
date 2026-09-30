# [M] When `ui.isAccessAllowed` is `undefined`, the `adminMeta` GraphQL query is publicly accessible

## Summary
Severity: Medium
Advisory: GHSA-9cvc-v7wm-992c
CVE: CVE-2023-40027
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-15
Source: https://github.com/advisories/GHSA-9cvc-v7wm-992c
Type: github-advisory

## Affected
- npm: `@keystone-6/core` — affected >=0 <5.5.1

## Details
### Summary
When `ui.isAccessAllowed` is `undefined`, the `adminMeta` GraphQL query is publicly accessible, that is to say, no session is required for the query.

This is different to the behaviour of the default AdminUI middleware, which by default will only be publicly accessible if a `session` strategy is not defined. 

### Impact
This vulnerability does not affect developers using the `@keystone-6/auth` package, or any users that have written their own `ui.isAccessAllowed` (that is to say, you are unaffected if `ui.isAccessAllowed` is defined).

This vulnerability does affect developers who thought that their `session` strategy will, by default, enforce that `adminMeta` is inaccessible by the public in accordance with that strategy; akin to the behaviour of the AdminUI middleware.

### Patches
This vulnerability has been patched in `@keystone-6/core` version `5.5.1`.

### Workarounds
You can opt to write your own `isAccessAllowed` to work-around this vulnerability.

### References
Pull request https://github.com/keystonejs/keystone/pull/8771

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-9cvc-v7wm-992c
- https://nvd.nist.gov/vuln/detail/CVE-2023-40027
- https://github.com/keystonejs/keystone/pull/8771
- https://github.com/keystonejs/keystone/commit/650e27e6e9b42abfb94c340c8470faf61f0ff284
- https://github.com/keystonejs/keystone
- https://github.com/keystonejs/keystone/releases/tag/2023-08-15
