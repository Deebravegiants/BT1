# [H] Open WebUI: shared-chat branch ignores access_type, allowing unauthorized file deletion

## Summary
Severity: High
Advisory: GHSA-26g9-27vm-x3q8
CVE: CVE-2026-45671
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-26g9-27vm-x3q8
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
### Summary

Any authenticated user can permanently delete files owned by other users via `DELETE /api/v1/files/{id}` when the target file is referenced in any shared chat. The `has_access_to_file()` authorization gate unconditionally grants access through its shared-chat branch. It checks neither the requesting user's identity nor the type of operation being performed. File UUIDs (which would otherwise be impractical to guess) are disclosed to any user with read access to a knowledge base via `GET /api/v1/knowledge/{id}/files`.

### Details

The root cause is in `has_access_to_file()` in [backend/open_webui/routers/files.py](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/files.py).

When a user calls `DELETE /api/v1/files/{file_id}`, the endpoint delegates authorization to `has_access_to_file(file_id, access_type="write", user=requesting_user)`. Inside that function, one branch checks whether the file is referenced in any shared chat:

```python
chats = Chats.get_shared_chats_by_file_id(file_id, db=db)
if chats:
    return True
```

This branch has two missing checks:

1. **No user check:** It asks "does any shared chat anywhere reference this file?", not "does the requesting user own or participate in that chat." Any authenticated user passes this check.
2. **No operation check:** The `access_type` parameter (`"write"` for delete) is accepted but never inspected. The branch returns `True` regardless of whether the caller is requesting read access or delete access.

The result: if any user has shared any chat that references a file, that file becomes deletable by every authenticated user on the instance.

The delete endpoint has no secondary ownership check (unlike the content-update endpoint), so this authorization bypass leads directly to permanent file removal from the database, disk, and all knowledge base associations.

**How an attacker obtains file UUIDs:**

UUIDs are impractical to brute-force, but they don't need to be. Any user with read access to a knowledge base can retrieve the file IDs of every document in it via `GET /api/v1/knowledge/{id}/files`. In deployments where knowledge bases are shared across teams (a common and intended use case), this gives any regular user a list of valid file UUIDs they can target.

**Suggested fix**:  gate the shared-chat branch on `access_type` so it only authorizes read operations:

```python
if access_type == "read":
    chats = Chats.get_shared_chats_by_file_id(file_id, db=db)
    if chats:
        return True
```

**Classification:**
- CWE-639: Authorization Bypass Through User-Controlled Key
- OWASP API1:2023: Broken Object Level Authorization
- CVSS 3.1: 5.7 — `AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H`

Tested on Open WebUI **0.8.3** using a default Docker configuration.

### PoC

**Prerequisites:**
- Default Open WebUI installation (Docker: `ghcr.io/open-webui/open-webui:main`)
- Two user accounts: a victim (any role) and an attacker (role: `user`)

**Setup (victim):**
1. Log in as the victim
2. Create a knowledge base and upload a document
3. Start a new chat, attach the KB file, and send a message
4. Share the chat using the share button

**Obtaining the file UUID (attacker):**

If the attacker has read access to the knowledge base (e.g. a shared team KB), the file UUID is available via:

```
GET /api/v1/knowledge/{kb_id}/files
```

This returns metadata for all files in the KB, including their UUIDs.

**Exploit (attacker):**

```bash
python3 poc.py --url http://<host>:3000 --file-id <target-file-uuid> -t <attacker-jwt>
```

The PoC script (attached as `poc.py`):
1. Authenticates as the attacker
2. Confirms the target file is accessible via `GET /api/v1/files/{id}/data/content`
3. Deletes the file via `DELETE /api/v1/files/{id}`
4. Verifies permanent deletion (HTTP 404 on subsequent GET)

No special tooling is required — the script uses only Python 3 standard library (`urllib`).

### Impact

**Who is affected:** Any multi-user Open WebUI deployment where chat sharing is enabled (the default). The attacker needs a valid account (any role) and a target file UUID, which is available through any shared knowledge base.

**What can happen:**
- **Permanent data destruction:** The file is removed from the database, disk, and all knowledge base associations with no recovery mechanism.
- **Knowledge base degradation:** If the file was part of a RAG knowledge base, that KB silently loses the document with no user-facing indication that content is missing.
- **No audit trail:** The delete operation does not record which user performed it.

Sharing a chat is a routine collaboration action. The current behavior means that doing so inadvertently makes every referenced file deletable by any authenticated user on the instance.

### Disclaimer on the use of AI powered tools 

The research and reporting related to this vulnerability was aided by AI tools. 

## Scope clarification

The root cause is the `has_access_to_file()` shared-chat branch returning `True` regardless of `access_type` or requesting user. The original PoC demonstrates DELETE (`access_type='write'`), but the same gate is what authorizes the read (`GET /api/v1/files/{id}`, `GET /api/v1/files/{id}/content`) and modify (`POST /api/v1/files/{id}/data/content/update`) endpoints. All three access modes are bypassed by the same function gap, so the practical impact is read + modify + delete on any file referenced by any shared chat.

## Resolution

Fixed in commit [2e52ad8ff](https://github.com/open-webui/open-webui/commit/2e52ad8ff2f8d9ed9f38f76e9bc19c8f92d91fc3) ("refac: shared chat"), first released in **v0.9.0** (Apr 2026). The shared-chat feature was refactored to introduce a dedicated `shared_chats` table and gate shared-chat access through `AccessGrants` (`resource_type='shared_chat'`). `has_access_to_file()` (now in `backend/open_webui/utils/access_control/files.py:68-80`) calls `AccessGrants.get_accessible_resource_ids` to filter the shared-chat IDs to only those the requesting user has an explicit grant on — ownership, group membership, or public share — before returning `True`

The new gate is permission-aware ('read' here) and user-aware, closing both the "any user passes" issue and the "access_type ignored" issue. Users on >= 0.9.0 are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-26g9-27vm-x3q8
- https://nvd.nist.gov/vuln/detail/CVE-2026-45671
- https://github.com/open-webui/open-webui/commit/2e52ad8ff2f8d9ed9f38f76e9bc19c8f92d91fc3
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
