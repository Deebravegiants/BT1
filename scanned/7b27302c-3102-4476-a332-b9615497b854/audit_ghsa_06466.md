# [M] Open WebUI: Upload `metadata.knowledge_id` bypasses the knowledge-base write-access check (read-only users can add files to KB)

## Summary
Severity: Medium
Advisory: GHSA-7r7x-gjvr-448g
CVE: CVE-2026-59217
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-7r7x-gjvr-448g
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
# Open WebUI upload metadata can add files to knowledge bases without write permission

## Summary

Open WebUI's file upload background processing trusts the client-supplied `metadata.knowledge_id` value and inserts a `knowledge_file` association before validating that the uploading user has write access to the target knowledge base.

A verified user with only read access to a knowledge base can upload an arbitrary file and set `metadata={"knowledge_id":"<target knowledge id>"}`. The normal `/api/v1/knowledge/{id}/file/add` endpoint correctly requires knowledge-base write access, but the upload auto-link path bypasses that authorization check.

The immediate result is unauthorized modification of the target knowledge base's file membership. The attached attacker-controlled file becomes visible through `/api/v1/knowledge/{id}/files`, and readers/owners of that knowledge base can retrieve the file through the normal file endpoints because file access is derived from `KnowledgeFile` membership.

## Affected Version

- Repository: `open-webui/open-webui`
- Tested source commit: `02dc3e689ceac915a870b373318b99c029ddf603`
- Package version observed in `package.json`: `0.9.6`
- Package name: `open-webui`

## Impact

A read-only knowledge-base collaborator can perform a write operation against that knowledge base by attaching arbitrary uploaded files.

Security impact:

- Unauthorized knowledge-base membership modification.
- Integrity impact on shared knowledge-base file listings.
- Attacker-controlled files become readable to other users who can read the target knowledge base.
- If an owner/admin later reprocesses or globally reindexes the knowledge base, the unauthorized file can be indexed into the knowledge collection, turning the membership bypass into RAG/content poisoning.

This is not an unauthenticated issue. It requires a verified Open WebUI account and a valid target knowledge-base ID. The clearest exploit path is a user who legitimately has read access to a knowledge base but not write access.

## Source Evidence

The normal single-file knowledge add endpoint checks write permission before processing or inserting the relationship:

- `backend/open_webui/routers/knowledge.py`
- `add_file_to_knowledge_by_id`
- Lines 714-728 reject callers who are not owner, admin, or granted `write` access.
- Lines 750-766 then process and insert the file only after that authorization gate.

The upload auto-link path does not perform the same check:

- `backend/open_webui/routers/files.py`
- `process_uploaded_file`
- Lines 178-186 read `knowledge_id` from upload metadata and immediately call `Knowledges.add_file_to_knowledge_by_id(...)`.
- Lines 187-192 call `process_file(... collection_name=knowledge_id ...)` after the insert.

The model method inserts the relationship without validating the caller's write access to the knowledge base:

- `backend/open_webui/models/knowledge.py`
- `add_file_to_knowledge_by_id`
- Lines 646-677 create and commit a `KnowledgeFile` row for the supplied `knowledge_id`, `file_id`, and `user_id`.

The later vector write check exists, but it runs too late:

- `backend/open_webui/routers/retrieval.py`
- `process_file`
- Lines 1587-1592 call `_validate_collection_access(..., access_type='write')` when a collection is supplied.

Because the unauthorized `KnowledgeFile` row is already committed before that check runs, the failed vector processing does not undo the knowledge-base file association. The upload code catches the exception at `backend/open_webui/routers/files.py` lines 194-195 and logs a warning while leaving the row in place.

The unauthorized relationship affects file access decisions:

- `backend/open_webui/utils/access_control/files.py`
- `has_access_to_file`
- Lines 41-53 grant file access when a file is associated with a knowledge base the user can access.

So once the attacker's file is inserted into the target `KnowledgeFile` table, target knowledge-base readers/owners can see and fetch that file through normal knowledge/file routes.

## Reproduction Steps

Use a local Open WebUI instance with two verified users:

1. As user `owner`, create a knowledge base.
2. Grant user `reader` read access to the knowledge base, but do not grant write access.
3. As `reader`, confirm the normal add-file endpoint is blocked:

```http
POST /api/v1/knowledge/<knowledge_id>/file/add
Authorization: Bearer <reader token>
Content-Type: application/json

{"file_id":"<reader-owned-file-id>"}
```

Expected and observed behavior for the normal route: it rejects the request because `reader` lacks knowledge-base write access.

4. As `reader`, upload a new file with the same target knowledge ID embedded in upload metadata:

```http
POST /api/v1/files/?process=true&process_in_background=false
Authorization: Bearer <reader token>
Content-Type: multipart/form-data

file=@attacker-note.txt
metadata={"knowledge_id":"<knowledge_id>"}
```

5. Observe that the upload request succeeds and returns the uploaded file record.
6. As `owner`, request the knowledge-base files:

```http
GET /api/v1/knowledge/<knowledge_id>/files
Authorization: Bearer <owner token>
```

7. Observe that `attacker-note.txt` appears in the target knowledge base even though `reader` did not have write access.
8. As `owner`, request the file content:

```http
GET /api/v1/files/<attacker_file_id>/content
Authorization: Bearer <owner token>
```

9. Observe that the file is retrievable because `has_access_to_file` derives access from the unauthorized knowledge-base membership.

## Expected Behavior

The upload auto-link path should enforce the same authorization contract as `/api/v1/knowledge/{id}/file/add`:

- The target knowledge base must exist.
- The caller must be the knowledge owner, an admin, or have `write` access.
- The supplied `directory_id`, if present, must belong to the target knowledge base.
- The `KnowledgeFile` association should only be inserted after authorization and processing succeed.

## Actual Behavior

`metadata.knowledge_id` causes `Knowledges.add_file_to_knowledge_by_id(...)` to insert a `KnowledgeFile` row before write authorization is checked. The later collection write validation can fail, but the unauthorized membership row remains committed.

## Suggested Fix

Move knowledge-base authorization before the insert in the upload auto-link path. The upload path should share the same write-access and directory validation logic used by the dedicated knowledge endpoints.

One safe pattern:

1. Load the target knowledge base.
2. Require owner/admin/write access before calling `Knowledges.add_file_to_knowledge_by_id`.
3. Validate that `directory_id`, if supplied, belongs to the same knowledge base.
4. Run vector processing before inserting the membership row, or wrap processing plus insertion in a transaction/compensating cleanup so a denied or failed process cannot leave a stale unauthorized row.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-7r7x-gjvr-448g
- https://nvd.nist.gov/vuln/detail/CVE-2026-59217
- https://github.com/open-webui/open-webui/pull/26001
- https://github.com/open-webui/open-webui/commit/b7626f05fb92b24ab923ad81a037071ebd5623d1
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
