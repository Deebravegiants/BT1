# [H] Tandoor Recipes — `amount`/`unit` bypass serializer in `food/{id}/shopping/`

## Summary
Severity: High
Advisory: CVE-2026-35489
Aliases: GHSA-8w8h-3pv2-3554
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35489
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.6.4, the POST /api/food/{id}/shopping/ endpoint reads amount and unit directly from request.data and passes them without validation to ShoppingListEntry.objects.create(). Invalid amount values (non-numeric strings) cause an unhandled exception and HTTP 500. A unit ID from a different Space can be associated cross-space, leaking foreign-key references across tenant boundaries. All other endpoints creating ShoppingListEntry use ShoppingListEntrySerializer, which validates and sanitizes these fields. This vulnerability is fixed in 2.6.4.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35489.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-8w8h-3pv2-3554
- https://nvd.nist.gov/vuln/detail/CVE-2026-35489
