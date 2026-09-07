# [M] Bypass of field access control in strapi-plugin-protected-populate

## Summary
Severity: Medium
Advisory: GHSA-6h67-934r-82g7
CVE: CVE-2023-48218
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-6h67-934r-82g7
Type: github-advisory

## Affected
- npm: `strapi-plugin-protected-populate` — affected >=0 <1.3.4

## Details
### Impact
Users are able to bypass the field level security. This means fields that they where not allowed to populate could be populated anyway even in the event that they tried to populate something that they don't have access to.

### Patches
This issue has been patched in 1.3.4

### Workarounds
None

## References
- https://github.com/strapi-community/strapi-plugin-protected-populate/security/advisories/GHSA-6h67-934r-82g7
- https://nvd.nist.gov/vuln/detail/CVE-2023-48218
- https://github.com/strapi-community/strapi-plugin-protected-populate/commit/05441066d64e09dd55937d9f089962e9ebe2fb39
- https://github.com/strapi-community/strapi-plugin-protected-populate
- https://github.com/strapi-community/strapi-plugin-protected-populate/releases/tag/v1.3.4
