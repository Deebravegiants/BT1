# [M] Tandoor Recipes's Unauthenticated Debug Parameter Leaks Full Raw SQL Queries Including Schema, Table Names, and Access Control Logic

## Summary
Severity: Medium
Advisory: CVE-2026-33153
Aliases: GHSA-f83r-v3h5-pchf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33153
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. In versions prior to 2.6.0, the Recipe API endpoint exposes a hidden `?debug=true` query parameter that returns the complete raw SQL query being executed, including all table names, column names, JOIN relationships, WHERE conditions (revealing access control logic), and multi-tenant space IDs. This parameter works even when Django's `DEBUG=False` (production mode) and is accessible to any authenticated user regardless of their privilege level. This allows a low-privilege attacker to map the entire database schema and reverse-engineer the authorization model. Version 2.6.0 patches the issue.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33153.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-f83r-v3h5-pchf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33153
