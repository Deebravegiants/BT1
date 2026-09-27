# [M] Directus `search` query parameter allows enumeration of non permitted fields

## Summary
Severity: Medium
Advisory: GHSA-7wq3-jr35-275c
CVE: CVE-2025-30352
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-26
Source: https://github.com/advisories/GHSA-7wq3-jr35-275c
Type: github-advisory

## Affected
- npm: `directus` — affected >=9.0.0-alpha.4 <11.5.0

## Details
### Summary

The `search` query parameter allows users with access to a collection to filter items based on fields they do not have permission to view. This allows the enumeration of unknown field contents.

### Details

The searchable columns (numbers & strings) are not checked against permissions when injecting the `where` clauses for applying the search query. This leads to the possibility of enumerating those un-permitted fields.

### PoC

- Create a collection with a string / numeric field, configure the permissions for the public role to not include the field created
- Create items with identifiable content in the not permitted field
- Query the collection and include the field content in the `search` parameter
- See that results are returned, even tho the public user does not have permission to view the field content

### Impact

This vulnerability is a very high impact, as for example Directus instances which allow public read access to the user avatar are vulnerable to have the email addresses, password hashes and potentially admin level access tokens extracted. The admin token and password hash extraction have a caveat, as string fields are only searched with a lower cased version of the search query.

## References
- https://github.com/directus/directus/security/advisories/GHSA-7wq3-jr35-275c
- https://nvd.nist.gov/vuln/detail/CVE-2025-30352
- https://github.com/directus/directus/commit/ac5a9964d9926f20dc063a74cb417dc7bbad676d
- https://github.com/directus/directus
