# [C] Strapi may leak sensitive data via relational filtering due to lack of query sanitization

## Summary
Severity: Critical
Advisory: GHSA-rjg2-95x7-8qmx
CVE: CVE-2026-27886
CWE: CWE-200, CWE-22, CWE-943
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rjg2-95x7-8qmx
Type: github-advisory

## Affected
- npm: `@strapi/strapi` — affected >=4.0.0 <5.37.0

## Details
### Summary of CVE-2026-27886 Vulnerability Details

- CVE: CVE-2026-27886
- CVSS v3.1 Vector: `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N` (9.3 — Critical)
- Affected Versions: `@strapi/strapi` <=5.36.1
- How to Patch: Immediately update your Strapi to >=5.37.0

### Description of CVE-2026-27886

Strapi versions prior to 5.37.0 did not sufficiently sanitize query parameters when filtering content via relational fields. An unauthenticated attacker could use the `where` query parameter on any publicly-accessible content-type with an `updatedBy` (or other admin-relation) field to perform a boolean-oracle attack against private fields on the joined `admin_users` table, including the `resetPasswordToken` field. Extracting an admin reset token via this oracle made full administrative account takeover possible without authentication.

When a filter such as `where[updatedBy][resetPasswordToken][$startsWith]=a` was applied to a public Content API endpoint, the underlying query generation performed a `LEFT JOIN` against the `admin_users` table and emitted a `WHERE` clause referencing the joined column. The query parameter sanitization layer did not block operator chains that traversed into relational target schemas the caller had no read permission on, allowing the response count to be used as a one-bit oracle on any admin-table field.

The patch introduces explicit query-parameter sanitization at the controller and service boundary via three new primitives: `strictParam`, `addQueryParams`, and `addBodyParams`. Operator chains that traverse into restricted relational targets are now rejected before reaching the database.

### IoC's for CVE-2026-27886

Indicators that an instance running an unpatched version may have been exploited:

- Server access logs containing query strings traversing into admin-relation private fields. Regex: `\?(.*&)?where\[(updatedBy|createdBy|publishedBy)\]\[(email|password|resetPasswordToken|confirmationToken|firstname|lastname|preferedLanguage)\]\[\$(startsWith|contains|eq|gt|lt|ge|le|in|notIn|notNull|null)\]=`
- High volume of public Content API requests from a single IP iterating through a hex alphabet (`0`-`9`, `a`-`f`) on the same content-type endpoint with progressively-longer filter values
- Subsequent `POST /admin/reset-password` calls using a reset token that the legitimate admin did not request
- Successful admin password change immediately following a burst of public Content API requests with `where[updatedBy]` query parameters
- Sustained burst of identical-shape requests with only the trailing character of the filter value varying

### Credit
Discovered by: James Doll - WildWest CyberSecurity
Contact: cve+2026-27886@wildwestcyber.com
Website: https://wildwestcyber.com
LinkedIn: https://www.linkedin.com/in/james-doll-273a61243

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-rjg2-95x7-8qmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27886
- https://github.com/strapi/strapi
