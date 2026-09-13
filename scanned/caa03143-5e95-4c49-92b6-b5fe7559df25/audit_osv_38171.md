# [H] Tandoor Recipes Affected by Private Recipe Exposure and Unauthorized Modification

## Summary
Severity: High
Advisory: CVE-2026-35045
Aliases: GHSA-v8x3-w674-55p5
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35045
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.6.4, the PUT /api/recipe/batch_update/ endpoint in Tandoor Recipes allows any authenticated user within a Space to modify any recipe in that Space, including recipes marked as private by other users. This bypasses all object-level authorization checks enforced on standard single-recipe endpoints (PUT /api/recipe/{id}/), enabling forced exposure of private recipes, unauthorized self-grant of access via the shared list, and metadata tampering. This vulnerability is fixed in 2.6.4.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35045.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-v8x3-w674-55p5
- https://nvd.nist.gov/vuln/detail/CVE-2026-35045
