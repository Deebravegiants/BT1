# [M] Open WebUI has Unauthorized File and Knowledge Base Content Access via RAG Vector Search

## Summary
Severity: Medium
Advisory: GHSA-h36f-rqpx-j5wx
CVE: CVE-2026-44560
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-h36f-rqpx-j5wx
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Unauthorized File and Knowledge Base Content Access via RAG Vector Search

## Affected Component

RAG source resolution in chat completion pipeline:
- `backend/open_webui/retrieval/utils.py` (lines 963-965, 1063-1068, 1126-1131 in `get_sources_from_items`)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with RAG functionality.

## Description

The `get_sources_from_items` function resolves file and knowledge base references into vector search queries during chat completion. Three of the five code paths perform vector store queries without any authorization check, allowing users to extract content from files and knowledge bases they do not have access to.

| Path | Lines | Access Check |
|------|-------|-------------|
| `type: "file"`, full-context | 1044-1050 | ✅ `has_access_to_file` |
| `type: "file"`, non-full-context (default) | 1063-1068 | ❌ None |
| `type: "collection"` | 1070-1118 | ✅ Present |
| `type: "text"` with `collection_name` | 963-965 | ❌ None |
| Bare `collection_name`/`collection_names` | 1126-1131 | ❌ None |

The three unprotected paths pass user-supplied collection names directly to `query_collection()`, which queries the vector store without any authorization. Collection names follow predictable formats: `file-<file_id>` for files and the knowledge base UUID for knowledge bases.

## CVSS 3.1 Breakdown

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector | Network (N) | Exploited remotely via chat completion API |
| Attack Complexity | Low (L) | Single API call with a known resource ID |
| Privileges Required | Low (L) | Requires a valid user account |
| User Interaction | None (N) | No victim interaction required |
| Scope | Unchanged (U) | Impact within the application's data boundary |
| Confidentiality | High (H) | Full content of private files/knowledge bases extractable |
| Integrity | None (N) | No data modification |
| Availability | None (N) | No denial of service |

## Attack Scenario

1. User A uploads a private document and uses it in RAG (the document is embedded into the vector store as collection `file-<file_id>`).
2. User A shares a chat or model referencing the file with User B, or User B otherwise obtains the file ID through a legitimate interaction.
3. User A later revokes User B's access to the file.
4. User B sends a chat completion request referencing the revoked file:
   ```json
   POST /api/chat/completions
   {
     "model": "any-accessible-model",
     "messages": [{"role": "user", "content": "What does this document say about pricing?"}],
     "files": [{"type": "file", "id": "<revoked_file_id>"}]
   }
   ```
5. The non-full-context path (default) constructs collection name `file-<id>` and queries the vector store with no access check.
6. Matching chunks are injected into the LLM context, and the response contains the victim's private file content.

The same attack works via `{"type": "text", "collection_name": "<knowledge_base_id>"}` for knowledge bases.

## Impact

- Access revocation is ineffective for RAG content — users who previously had access can continue extracting file and knowledge base content indefinitely
- Private document content can be systematically extracted through targeted queries
- Breaks the access control model for files and knowledge bases at the RAG layer

## Preconditions

- Attacker must know the file ID or knowledge base ID (UUID) of the target resource
- The target file/knowledge base must have been processed into the vector store
- Attacker must have a valid user account

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-h36f-rqpx-j5wx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44560
- https://github.com/open-webui/open-webui
