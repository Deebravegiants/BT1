# [M] Open WebUI's Mass Assignment via Pydantic extra='allow' Allows Creating Folders in Other Users' Accounts

## Summary
Severity: Medium
Advisory: GHSA-hr43-rjmr-7wmm
CVE: CVE-2026-44550
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-hr43-rjmr-7wmm
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Mass Assignment via Pydantic extra='allow' Allows Creating Folders in Other Users' Accounts

## Affected Component

Folder creation endpoint and form model:
- `backend/open_webui/models/folders.py` (lines 72-77, `FolderForm` with `extra='allow'`)
- `backend/open_webui/models/folders.py` (lines 95-106, `insert_new_folder` dict construction)
- `backend/open_webui/routers/folders.py` (line 119, `create_folder` endpoint)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions since `FolderForm` adopted `extra='allow'`.

## Description

`FolderForm` uses `model_config = ConfigDict(extra='allow')`, which permits arbitrary fields to pass through Pydantic validation and be included in `model_dump(exclude_unset=True)`. In `insert_new_folder`, the server-assigned `user_id` is placed at the start of the dict and then overwritten by the spread of form data:

```python
# models/folders.py:95-106
folder = FolderModel(
    **{
        'id': id,                                              # server
        'user_id': user_id,                                    # server — overwritten below
        **(form_data.model_dump(exclude_unset=True) or {}),    # user-controlled (extra='allow')
        'parent_id': parent_id,
        'created_at': int(time.time()),
        'updated_at': int(time.time()),
    }
)
```

Because `FolderModel` declares `user_id: str` as a real field (not just a form extra), any attacker-supplied `user_id` in the POST body is accepted by the model and persisted on the `Folder` row.

## Attack Scenario

1. Attacker discovers a victim's user ID. User UUIDs commonly leak via the user search endpoint (`GET /api/v1/users/search`, intentionally accessible to verified users for sharing UI), shared chat metadata, or channel member lists.
2. Attacker sends:
   ```
   POST /api/v1/folders/
   {
     "name": "Important: Click here",
     "user_id": "<victim_user_id>",
     "meta": {"icon": "warning"},
     "data": {...}
   }
   ```
3. Pydantic accepts the extra `user_id` field (allowed by `extra='allow'`).
4. `insert_new_folder` spreads the form data over the server-set `'user_id': user_id`, overwriting it with the attacker's value.
5. The `Folder` row is persisted with `user_id = <victim_user_id>`.
6. The victim sees the attacker-planted folder in their UI on next load because `GET /api/v1/folders/` filters by the viewer's own `user_id`.

The attacker can repeat this to plant multiple folders, use crafted `name` values for phishing ("Click here to recover account" / "Security alert"), and abuse the `meta` and `data` fields to add visual elements that further mimic legitimate content.

## Impact

- Unauthorized write into victim's folder tree
- Phishing surface: attacker-controlled `name`, `meta`, and `data` render in the victim's UI in a trusted context
- DoS / spam: attacker can flood a victim with arbitrary folders; victim must manually delete each one
- Attacker cannot read the folder back — all read paths filter by the caller's own `user_id` — so confidentiality is preserved, but integrity and trust are compromised

## Preconditions

- Attacker must have an authenticated account with `features.folders` permission (default for all users)
- Attacker must know or guess the victim's user UUID (obtainable through various non-sensitive endpoints)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-hr43-rjmr-7wmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44550
- https://github.com/open-webui/open-webui
