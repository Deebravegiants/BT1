# [M] Winter: Authenticated IDOR in backend FileUpload widget allows cross-user access to attachment metadata

## Summary
Severity: Medium
Advisory: GHSA-3277-h8g9-qj5f
CVE: CVE-2026-54256
CWE: CWE-284, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-3277-h8g9-qj5f
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=0 <1.2.13

## Details
### Impact

The backend `FileUpload` form widget trusted an attacker-controlled `file_id` POST parameter when resolving the attachment it operates on. The lookup (`FileUpload::getFileRecord()`) resolved the posted id against the global `system_files` table without verifying that the file belonged to the widget's own relation, parent record, or deferred-binding session.

Any authenticated backend user who can reach a form containing a `fileupload` field — including the built-in **My Account** avatar field, which requires no specific backend permission — could therefore target a `System\Models\File` record belonging to another user or record and:

- modify its `title` and `description` via `onSaveAttachmentConfig`, and
- change its `sort_order` via `onSortAttachments` (which passed posted ids
  straight to `setSortableOrder()`, an unscoped `UPDATE ... WHERE id = ?`).

The same unscoped lookup is reached by `onLoadAttachmentConfig`, `onSaveAttachmentConfig`, and `onRemoveAttachment`. Because all attachments share the single `System\Models\File` model and `system_files` table, an attacker was not limited to other users' avatars — any attachment on any model could be referenced by id. Attachment ids are sequential integers and are easily enumerated.

The confirmed impact is unauthorized integrity modification of arbitrary attachment metadata and ordering.

CSRF tokens are still verified on all POST requests, so an attacker must be authenticated to the backend with a valid session. To exploit this issue an attacker needs a backend account with any level of access.

### Patches

The `FileUpload` widget now scopes every `file_id` lookup to the widget's own relation, including any files bound through the current deferred-binding session, so a posted id can no longer reference an unrelated `System\Models\File` record:

- `getFileRecord()` resolves the id through `getRelationObject()->withDeferred($this->sessionKey)->find(...)` rather than the global file model. This covers `onLoadAttachmentConfig`, `onSaveAttachmentConfig`, and `onRemoveAttachment`.
- `onSortAttachments()` intersects the posted ids with the ids that actually belong to the relation before calling `setSortableOrder()`.

This security issue has been fixed as of **v1.2.13** (commit [`9cb0ae5f9d837db141ab111c6a7de8eed9603d25`](https://github.com/wintercms/winter/commit/9cb0ae5f9d837db141ab111c6a7de8eed9603d25)).

### Workarounds

There is no supported workaround other than upgrading. If you cannot upgrade immediately, you may apply the fix manually in `modules/backend/formwidgets/FileUpload.php`:

1. In `getFileRecord()`, replace `$this->getRelationModel()->find(post('file_id'))` with `$this->getRelationObject()->withDeferred($this->sessionKey)->find(post('file_id'))`.
2. In `onSortAttachments()`, filter the posted `sortOrder` ids to those returned by `$this->getRelationObject()->withDeferred($this->sessionKey)->pluck($keyName)` before calling `setSortableOrder()`.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-3277-h8g9-qj5f
- https://github.com/wintercms/winter/security/advisories/GHSA-qq9m-vfv4-pj5w
- https://github.com/wintercms/winter/commit/9cb0ae5f9d837db141ab111c6a7de8eed9603d25
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
