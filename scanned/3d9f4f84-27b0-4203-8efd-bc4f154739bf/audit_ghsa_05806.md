# [M] django CMS: Clipboard copy IDOR discloses unauthorized plugin content

## Summary
Severity: Medium
Advisory: GHSA-4xfr-4p46-gc6p
CVE: CVE-2026-54622
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-4xfr-4p46-gc6p
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.8

## Details
### Summary
  The clipboard copy paths of the `copy_plugins` admin endpoint validate only   the target (the user's own clipboard) and skip source-side authorization. A staff user can copy plugins out of a placeholder they have no permission on   into their clipboard, then read the (secret) content.

  ### Details
  In `cms/admin/placeholderadmin.py`, `_copy_plugin_to_clipboard` and   `_copy_placeholder_to_clipboard` check `has_copy_plugins_permission`, which only  evaluates `request.toolbar.clipboard.has_add_plugins_permission(...)` — the
  clipboard belongs to the requesting user, and `check_source` is likewise  applied only to the clipboard. The source placeholder identified by the  attacker-supplied `source_placeholder_id` / `source_plugin_id` is never  authorization-checked. (The placeholder-to-placeholder copy path,  `has_copy_from_placeholder_permission`, correctly checks both sides.)

  ### Impact
  A staff user holding the global add permission for a plugin type, but with no  access to a given placeholder/page, can copy that placeholder's plugins into  their own clipboard and read content (e.g. link names/URLs, text) they cannot  reach through the normal edit endpoints.

  Requires `CMS_PERMISSION=True` with per-placeholder/page restrictions.

  ### Patches
  Fixed in 5.0.8: the clipboard copy paths now also verify   source-side permission (`has_add_plugins_permission` + `check_source` on the  source placeholder), matching placeholder-to-placeholder copy.

  ### Workarounds
  None. Upgrade is recommended.

  ### Credits
  Reported by the security team at the University of Sydney ([@reporter]).

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-4xfr-4p46-gc6p
- https://github.com/django-cms/django-cms/pull/8645
- https://github.com/django-cms/django-cms/commit/7642a98ab3170793c0b27b4125dd1f3d318b8a1c
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.8
