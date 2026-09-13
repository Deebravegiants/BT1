# [M] Tandoor Recipes Affected by Denial of Service via Recipe Import

## Summary
Severity: Medium
Advisory: CVE-2026-27460
Aliases: GHSA-w8pq-4pwf-r2m8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-27460
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.6.5, a critical Denial of Service (DoS) vulnerability was in the recipe import functionality. This vulnerability allows an authenticated user to crash the server or make a significantly degrade its performance by uploading a large size ZIP file (ZIP Bomb). This vulnerability is fixed in 2.6.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27460.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-w8pq-4pwf-r2m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27460
