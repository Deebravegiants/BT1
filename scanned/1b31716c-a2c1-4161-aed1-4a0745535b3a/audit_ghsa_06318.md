# [M] django CMS: Structure endpoint bypasses page-view permission

## Summary
Severity: Medium
Advisory: GHSA-vgxm-h9gx-h9w7
CVE: CVE-2026-54624
CWE: CWE-285, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-vgxm-h9gx-h9w7
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.8

## Details
### Summary
The structure-board endpoint (`render_object_structure`) renders a page's plugin structure without verifying that the requesting user is allowed to view the page. The edit and preview endpoints enforce this via `render_page()`, but the structure endpoint does not, allowing a low-privileged staff user to read the plugin structure of a view-restricted page.

### Details
`render_object_structure` (in `cms/views.py`) loads the `PageContent` object and renders `cms/toolbar/structure.html` directly. Unlike `render_object_endpoint` (used by edit/preview), which renders through `render_pagecontent` → `render_page` and calls `user_can_view_page(request.user, page)` (returning 404 when the user may not view the page), the structure endpoint performs no page-level authorization.

The rendered structure board includes each plugin's `get_short_description()`  (e.g. link names/URLs, text snippets), so the content of a restricted page is disclosed, not just its shape.

### Impact
A staff user (any account with `is_staff=True`) who lacks view permission on a  view-restricted page can retrieve that page's plugin structure and short descriptions by requesting the structure endpoint with the page's content-type id and object id.

This only applies when `CMS_PERMISSION=True` and the page has view restrictions (or `CMS_PUBLIC_FOR='staff'`). Sites without per-page view restrictions are not affected.

### Patches
Fixed in 5.0.8: the structure endpoint now enforces `user_can_view_page()` for `PageContent` objects, matching edit/preview.

### Workarounds
None other than restricting staff access. Upgrade is recommended.

### Credits
Reported by the security team at the University of Sydney ([@reporter]).

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-vgxm-h9gx-h9w7
- https://github.com/django-cms/django-cms/pull/8645
- https://github.com/django-cms/django-cms/commit/7642a98ab3170793c0b27b4125dd1f3d318b8a1c
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.8
