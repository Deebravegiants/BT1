# [H] Tandoor Recipes — CustomIsShared permits DELETE/PUT on RecipeBook by shared (read-only) users

## Summary
Severity: High
Advisory: CVE-2026-35488
Aliases: GHSA-xvmf-cfrq-4j8f
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35488
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.6.4, RecipeBookViewSet and RecipeBookEntryViewSet use CustomIsShared as an alternative permission class, but CustomIsShared.has_object_permission() returns True for all HTTP methods — including DELETE, PUT, and PATCH — without checking request.method in SAFE_METHODS. Any user who is in the shared list of a RecipeBook can delete or overwrite it, even though shared access is semantically read-only. This vulnerability is fixed in 2.6.4.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35488.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-xvmf-cfrq-4j8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-35488
