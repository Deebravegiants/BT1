# [M] Craft CMS: Authorization bypass: view-only Categories user can modify category structure via structures/move-element

## Summary
Severity: Medium
Advisory: GHSA-xxpx-f366-4xpq
CVE: CVE-2026-72785
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-xxpx-f366-4xpq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.6

## Details
A control-panel user who holds only the viewCategories permission for a category group (and not saveCategories) can permanently modify that group's category structure — reordering and re-parenting categories via the structures/move-element action.

A read-time authorization grant that a write endpoint later trusts. For categories, the structureEditable flag is computed from the view permission (`src/elements/Category.php:205`) instead of the save permission (entries correctly use saveEntries — `src/elements/Entry.php:341`). When the read-only category index renders, `craft\base\Element::indexHtml()` calls `Craft::$app->getSession()->authorize('editStructure:<structureId>');` StructuresController then authorizes the structure-mutating action solely on that session grant, with no canSave re-check.

Verified on Craft CMS 5.10.5. Same class as the moderate-severity authorization bypasses fixed in 5.10.3 and 5.10.5; this is a distinct, unpatched instance.

## Impact

A low-privileged, authenticated user (view-only on a category group) can persistently alter the sibling ordering and parent/child nesting of the category taxonomy. Because a category’s URI is derived from its position in the structure (ancestor slugs), moving a category changes its URL and the URLs of its descendants, and can corrupt any navigation/menus built from the category tree. This is an integrity/broken access-control issue: content that the user has no permission to modify is being modified. No confidentiality impact and no RCE; scope is content/taxonomy integrity.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-xxpx-f366-4xpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72785
- https://github.com/craftcms/cms/commit/eb63721b8476ef53f21d7de53d156eef531cb57d
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.2
- https://github.com/craftcms/cms/releases/tag/5.10.6
- https://www.vulncheck.com/advisories/craft-cms-before-authorization-bypass-via-structures-move-element
