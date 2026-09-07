# [M] Winter: Broken access control in `Cms\Controllers\Index` allows cross-template actions and unauthorized asset uploads

## Summary
Severity: Medium
Advisory: GHSA-5c4f-9pq9-6c77
CVE: CVE-2026-32639
CWE: CWE-280
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-5c4f-9pq9-6c77
Type: github-advisory

## Affected
- Packagist: `winter/wn-cms-module` — affected >=0 <1.2.13

## Details
### Impact

Affected versions of Winter CMS did not enforce per-template-type permission checks in the CMS section's AJAX handlers. The CMS controller (`Cms\Controllers\Index`) used OR-logic across its five permissions (`cms.manage_pages`, `cms.manage_partials`, `cms.manage_layouts`, `cms.manage_content`, `cms.manage_assets`) to control access to the section as a whole, but individual handlers such as `onSave()`, `onDelete()`, and `onDeleteTemplates()` did not verify that the authenticated user holds the specific permission corresponding to the requested template type.

This allowed a backend user with any single Theme Editor permission (e.g. `cms.manage_pages`) to craft AJAX requests targeting template types outside their authorized scope — for example, deleting layouts, modifying partials, or reading content files.

In addition, the `AssetList` widget was registered for all users who passed the controller gate regardless of whether they held the `cms.manage_assets` permission, and its `onUpload()` handler was missing the `validateRequestTheme()` call that is present on all other mutating handlers in the same widget. This allowed unauthorized file uploads into the active theme's asset directory.

To actively exploit this security issue, an attacker would need access to the Backend with a user account with any of the following permissions:

- `cms.manage_pages`
- `cms.manage_partials`
- `cms.manage_layouts`
- `cms.manage_content`
- `cms.manage_assets`

The Winter CMS maintainers strongly recommend that all Winter CMS sites that rely on granular CMS permission assignments (specifically users with only access to `cms.manage_content` to only be able to edit content files through the Theme Editor) to update immediately.

### Patches

Per-template-type permission checks are now enforced on all Theme Editor AJAX handlers, the `AssetList` widget is only registered for users with the `cms.manage_assets` permission, and `onUpload()` now includes theme validation consistent with the other mutating handlers.

This security issue has been fixed as of v1.2.13.

### Workarounds

If users cannot upgrade, they may apply the following changes to their Winter CMS installation manually to resolve this issue:

1. In `modules/cms/controllers/Index.php`, wrap each widget registration in the constructor with the corresponding `hasAccess()` check, and add a `validateRequestType()` call to the `index_onOpenTemplate()`, `onSave()`, `onCreateTemplate()`, `onDeleteTemplates()`, `onDelete()`, `onCommit()`, and `onReset()` handlers that verifies the user holds the permission for the requested template type.
2. In `modules/cms/widgets/AssetList.php`, add a `$this->validateRequestTheme()` call at the top of the `onUpload()` method.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-5c4f-9pq9-6c77
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
