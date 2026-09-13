# [M] Open WebUI: Model meta.knowledge read-only file access can be upgraded to file write/delete

## Summary
Severity: Medium
Advisory: GHSA-2xwm-4h2q-ggfx
CVE: CVE-2026-59212
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-2xwm-4h2q-ggfx
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.6 <0.10.0

## Details
## Summary

Current `main` and `v0.9.6` still allow an authenticated user to turn read-only access to another user's file into write/delete access by attaching that file ID to an attacker-controlled workspace model.

This is an incomplete-fix variant of `GHSA-vjqm-6gcc-62cr`. The current fix adds `_verify_knowledge_file_access()`, but the validator only checks `has_access_to_file(file_id, "read", user)`. The file write/delete routes later trust `has_access_to_file(file_id, "write", user)`, and that function grants access through any writable model whose `meta.knowledge` contains the file ID.

The PoV includes a negative control showing the current validator rejects an inaccessible arbitrary file ID. The residual issue is narrower: a file ID that is readable only through a KB read grant is accepted into direct model file metadata, then the same model metadata satisfies later file write/delete checks.

## Technical Details

`backend/open_webui/routers/models.py::_verify_knowledge_file_access()` accepts model `meta.knowledge` file entries when the caller can read the file:

```python
if not await has_access_to_file(file_id, 'read', user, db=db):
    raise HTTPException(...)
```

`backend/open_webui/utils/access_control/files.py::has_access_to_file()` then uses attacker-writable model metadata as a source for any requested access type:

```python
for model in await Models.get_models_by_user_id(user.id, permission=access_type, db=db):
    knowledge_items = getattr(model.meta, 'knowledge', None) or []
    for item in knowledge_items:
        if isinstance(item, dict) and item.get('type') == 'file' and item.get('id') == file.id:
            return True
```

For `access_type="write"`, the attacker-owned model satisfies the model query, so the victim file becomes writable even though the attacker only had read access through the KB grant.

This crosses another user's integrity and availability boundary, not just the attacker's own account. Before model metadata is involved, the attacker can read the file through a KB grant but cannot write it. After the model metadata entry is accepted, the same file becomes writable/deletable.

The official docs distinguish attached knowledge permissions: knowledge-base collections may use explicit read grants, while individual files are owner/admin-only. This issue lets a read grant to a KB become direct write/delete authority over an individual file.

This is also consistent with the documented RBAC model: resource grants have separate `read` and `write` permissions, where write means the user can update or delete the resource. The exploit starts from a read-only KB grant and reaches file write/delete without a corresponding file owner/admin/write authorization.

The required Models workspace access is not root-equivalent in Open WebUI's documentation. The policy's root-equivalent warning applies to Tools/Functions code execution. This report does not use Tools/Functions, custom Python, admin actions, or a legacy-only path.

## Impact

An authenticated non-admin user with Models workspace access and read-only access to a victim file through a knowledge-base grant can create/import/update a model that references the file, then rename, overwrite, or delete the victim user's file through write-gated file routes.

Confirmed sinks in current head:

- `POST /api/v1/files/{id}/rename`
- `POST /api/v1/files/{id}/data/content/update`
- `DELETE /api/v1/files/{id}`

Suggested severity: High.

Suggested CVSS:

```text
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H
```

Suggested CWE:

```text
CWE-863: Incorrect Authorization
```

I am not claiming Critical severity because the attacker must be authenticated, must have Models workspace access, and must already have read-only access to the victim file through a KB grant. The High score is based on the post-condition: that limited read access becomes destructive cross-user file write/delete.

## Appendix: AI Disclosure

## Appendix: Local PoV

The PoV is local-only. It does not start a server, send network traffic, or use a real database. It loads and executes the current-head function bodies for:

- `has_access_to_file()`
- `_verify_knowledge_file_access()`
- `delete_file_by_id()`

Run from the harness root:

```bash
uv run python attached-evidence/poc/pov_openwebui_model_file_read_to_write.py
```

Observed output:

```json
{
  "confirmed": true,
  "control_inaccessible_file_rejected_by_validator": true,
  "control_read_allowed_via_kb_read_grant": true,
  "control_write_allowed_before_model_laundering": false,
  "model_metadata_validator_passed_with_read_only_access": true,
  "write_allowed_after_attacker_owned_model_contains_file": true,
  "delete_route_result": {
    "message": "File deleted successfully"
  },
  "deleted_file_ids": [
    "victim-file"
  ]
}
```

This demonstrates expected versus actual behavior:

- Expected: a user with only read access through a KB grant cannot mutate the victim file.
- Actual: after the read-only file ID is accepted into attacker-owned model metadata, the same user satisfies the file write/delete guard and deletes the victim file.

## Appendix: Remediation

Recommended defense-in-depth fix:

1. In `_verify_knowledge_file_access()`, require direct file ownership or admin for `type: "file"` model knowledge entries. Do not accept indirect KB read access as sufficient authority to attach an individual file to a model.
2. In `has_access_to_file()`, do not let the model `meta.knowledge` branch grant write access to files. Model-attached knowledge should be read-only unless the caller separately owns/administers the underlying file or has an explicit write-capable file authorization path.
3. Add regression tests covering the KB-read control, the blocked model attach, and rename/update/delete denial for the victim file.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-2xwm-4h2q-ggfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-59212
- https://github.com/open-webui/open-webui/pull/26032
- https://github.com/open-webui/open-webui/commit/17df0264929514599dbcb21c6578bcdfa204b04d
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
