# [M] Open WebUI Vulnerable to Unauthenticated RAG Configuration Disclosure

## Summary
Severity: Medium
Advisory: GHSA-65pg-qhhw-mxwg
CVE: CVE-2026-45397
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-65pg-qhhw-mxwg
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
**Vulnerability Type:** Information Disclosure / Missing Authentication  
**Severity:** Medium  
**Component:** `backend/open_webui/routers/retrieval.py` — `get_status()` (`GET /`)  
**Affected Endpoint:** `GET /api/v1/retrieval/`  
**Affected Version:** Open WebUI `main` branch — confirmed unpatched through **v0.9.2**  
**Authentication Required:** None — internet-facing with zero credentials  
**CVSSv3.1 Score:** 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)

---

## Summary

`GET /api/v1/retrieval/` returns live RAG pipeline configuration to any unauthenticated HTTP client. No `Authorization` header, cookie, or API key is required. Every adjacent endpoint on the same router (`/embedding`, `/config`) is correctly guarded by `get_admin_user` making this a targeted omission.

---

## Root Cause

`backend/open_webui/routers/retrieval.py:262`

```python
@router.get('/')
async def get_status(request: Request):   # ← no Depends(get_verified_user)
    return {
        'status': True,
        'CHUNK_SIZE': request.app.state.config.CHUNK_SIZE,
        'CHUNK_OVERLAP': request.app.state.config.CHUNK_OVERLAP,
        'RAG_TEMPLATE': request.app.state.config.RAG_TEMPLATE,
        'RAG_EMBEDDING_ENGINE': request.app.state.config.RAG_EMBEDDING_ENGINE,
        'RAG_EMBEDDING_MODEL': request.app.state.config.RAG_EMBEDDING_MODEL,
        'RAG_RERANKING_MODEL': request.app.state.config.RAG_RERANKING_MODEL,
        'RAG_EMBEDDING_BATCH_SIZE': request.app.state.config.RAG_EMBEDDING_BATCH_SIZE,
        'ENABLE_ASYNC_EMBEDDING': request.app.state.config.ENABLE_ASYNC_EMBEDDING,
        'RAG_EMBEDDING_CONCURRENT_REQUESTS': request.app.state.config.RAG_EMBEDDING_CONCURRENT_REQUESTS,
    }
```

Compare with every adjacent endpoint on the same router:

```python
@router.get('/embedding')
async def get_embedding_config(request: Request, user=Depends(get_admin_user)):  # ✅

@router.get('/config')
async def get_rag_config(request: Request, user=Depends(get_admin_user)):        # ✅
```

---

## Proof Of Concept — No Token Required

```bash
curl -s http://TARGET/api/v1/retrieval/
```

```json
{
  "status": true,
  "CHUNK_SIZE": 1000,
  "CHUNK_OVERLAP": 100,
  "RAG_TEMPLATE": "### Task:\nRespond to the user query using the provided context...\n<context>\n{{CONTEXT}}\n</context>",
  "RAG_EMBEDDING_ENGINE": "",
  "RAG_EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
  "RAG_RERANKING_MODEL": "",
  "RAG_EMBEDDING_BATCH_SIZE": 1,
  "ENABLE_ASYNC_EMBEDDING": true,
  "RAG_EMBEDDING_CONCURRENT_REQUESTS": 0
}
```

---

## Disclosed Information and Its Value to an Attacker

| Field | What it reveals |
|---|---|
| `RAG_EMBEDDING_ENGINE` | Backend type (OpenAI, Ollama, Azure, etc.) |
| `RAG_EMBEDDING_MODEL` | Exact model name — reveals embedding model |
| `RAG_RERANKING_MODEL` | Reranker in use — reveals reranker |
| `RAG_TEMPLATE` | **RAG template** — exposes the RAG template |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Chunking parameters — enables exact reconstruction of how documents are split and retrieved |

---

## Attack Scenario

1. Attacker sends one unauthenticated HTTP GET to `/api/v1/retrieval/`.
2. Response reveals the embedding model and chunking parameters.
3. Attacker uses the exact chunk size/overlap to craft RAG poisoning payloads that are guaranteed to be retrieved.

---

## Impact

1. **RAG template disclosure**
2. **Infrastructure fingerprinting** — embedding engine and model name reveal the AI stack to an internet scanner
3. **RAG attack surface mapping** — chunk parameters enable precise calculation of retrieval boundaries
4. **Zero-effort recon** — no brute force, no credentials, no rate-limit concern. Single request from any IP.

---

## Recommended Fix

Add `get_verified_user` dependency (or `get_admin_user` for stricter control):

```python
# BEFORE (vulnerable)
@router.get('/')
async def get_status(request: Request):


# AFTER
@router.get('/')
async def get_status(request: Request, user=Depends(get_verified_user)):
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-65pg-qhhw-mxwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45397
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
