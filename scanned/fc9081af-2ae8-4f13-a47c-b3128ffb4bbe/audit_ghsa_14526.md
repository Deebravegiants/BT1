# [M] Directus vulnerable to extraction of password hashes through export querying

## Summary
Severity: Medium
Advisory: GHSA-m5q3-8wgf-x8xf
CVE: CVE-2023-27481
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-m5q3-8wgf-x8xf
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <9.16.0

## Details
### Impact

Users with read access to the `password` field in `directus_users` can extract the argon2 password hashes by brute forcing the export functionality combined with a `_starts_with` filter. This allows the user to enumerate the password hashes.

### Patches

The problem has been patched by preventing any hashed/concealed field to be filtered against with the `_starts_with` or other string operator.

### Workarounds

Ensuring that no user has `read` access to the `password` field in `directus_users` is sufficient to prevent this vulnerability. 


### For more information
If you have any questions or comments about this advisory:
* Open a Discussion in [directus/directus](https://github.com/directus/directus/discussions/new)
* Email us at [security@directus.io](mailto:security@directus.io)

## References
- https://github.com/directus/directus/security/advisories/GHSA-m5q3-8wgf-x8xf
- https://nvd.nist.gov/vuln/detail/CVE-2023-27481
- https://github.com/directus/directus/pull/14829
- https://github.com/directus/directus/pull/15010
- https://github.com/directus/directus
