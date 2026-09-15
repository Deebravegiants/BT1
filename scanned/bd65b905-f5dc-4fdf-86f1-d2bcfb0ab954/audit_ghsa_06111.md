# [H] django CMS: Plugin move endpoint allows cyclic reparenting (DoS)

## Summary
Severity: High
Advisory: GHSA-8jj7-4v57-frf5
CVE: CVE-2026-54623
CWE: CWE-674, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-8jj7-4v57-frf5
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.8

## Details
### Summary
The `move_plugin` admin endpoint does not prevent a plugin from being   reparented under itself or one of its own descendants. Doing so creates a  cycle in the plugin tree, after which the recursive descendant/ancestor SQL  queries loop without terminating, stalling the request worker.

### Details
`move_plugin` (in `cms/admin/placeholderadmin.py`) accepts a  `plugin_parent` POST parameter and, for an in-placeholder move, sets the  plugin's parent to the target without any cycle/ancestor check. If the target  parent is a descendant of the moved plugin, the resulting `parent_id` graph  contains a cycle.

Descendant and ancestor traversal is implemented with `WITH RECURSIVE` CTEs  (`_get_descendants_cte` / `_get_ancestors_cte` in `cms/models/pluginmodel.py`)  that have no cycle clause or depth limit. On a cyclic tree these recurse  indefinitely (PostgreSQL/SQLite) or error at the recursion limit (MySQL).  `get_descendants()` is invoked while building the move response and on  subsequent operations on the affected subtree.

### Impact
An authenticated staff user with permission to change plugins in at least one   placeholder can corrupt that placeholder's plugin tree, causing requests that  traverse it (rendering, copy, delete) to hang and consume application workers  (denial of service). The tree is also left in a corrupted state.

Requires `CMS_PERMISSION`/plugin-change permission on a placeholder.

### Patches
Fixed in 5.0.8: `move_plugin` now rejects (HTTP 400) any move  that would place a plugin inside itself or one of its descendants, before any  tree mutation or traversal.

### Workarounds
None. Upgrade is recommended.

### Credits
Reported by the security team at the University of Sydney ([@reporter]).

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-8jj7-4v57-frf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54623
- https://github.com/django-cms/django-cms/pull/8645
- https://github.com/django-cms/django-cms/commit/7642a98ab3170793c0b27b4125dd1f3d318b8a1c
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.8
