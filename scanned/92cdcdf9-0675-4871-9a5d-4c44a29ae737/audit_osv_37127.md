# [M] Tandoor Recipes has Cross-Space IDOR in SyncViewSet.query_synced_folder: missing space scoping on get_object_or_404

## Summary
Severity: Medium
Advisory: CVE-2026-28503
Aliases: GHSA-6qpw-gwcq-68fv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-28503
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. In versions prior to 2.6.0, the `SyncViewSet.query_synced_folder()` action in `cookbook/views/api.py` (line 903) fetches a Sync object using `get_object_or_404(Sync, pk=pk)` without including `space=request.space` in the filter. This allows an admin user in Space A to trigger sync operations (Dropbox/Nextcloud/Local import) on Sync configurations belonging to Space B, and view the resulting sync logs. Version 2.6.0 patches the issue.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28503.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-6qpw-gwcq-68fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-28503
