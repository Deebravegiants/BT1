# [M] Open WebUI vulnerable to Global Knowledge Base Enumeration via knowledge-bases Meta-Collection

## Summary
Severity: Medium
Advisory: GHSA-6c2x-gcp3-gp73
CVE: CVE-2026-44557
CWE: CWE-200, CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-6c2x-gcp3-gp73
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Global Knowledge Base Enumeration via knowledge-bases Meta-Collection

## Affected Component

Retrieval collection access validation:
- `backend/open_webui/routers/retrieval.py` (lines 2330-2355, `_validate_collection_access`)
- `backend/open_webui/routers/retrieval.py` (query endpoints, e.g. `POST /query/doc`)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with the knowledge base subsystem.

## Description

The `_validate_collection_access` function uses an incomplete allowlist that only enforces ownership checks for collections matching `user-memory-*` and `file-*` patterns. All other collection names pass through unchecked — including the system-level `knowledge-bases` meta-collection, which stores the IDs, names, and descriptions of every knowledge base on the instance.

Any authenticated user can query this meta-collection directly via the retrieval query endpoints to obtain a global index of all knowledge bases across all users.

```python
# retrieval.py:2330-2355 — incomplete collection allowlist
def _validate_collection_access(user, collection_name, ...):
    if collection_name.startswith('user-memory-'):
        # Check user-memory ownership
        ...
    elif collection_name.startswith('file-'):
        # Check file access
        ...
    # Everything else (including "knowledge-bases") passes through unchecked
```

This finding is the enabler for the KB destruction (`process/web`), KB content injection (`process/file`), and RAG vector search access bypass findings — all of which require knowing a target KB's UUID. Without this enumeration, UUIDs are random and practically unguessable; with it, UUIDs across the entire instance are trivially obtained.

## CVSS 3.1 Breakdown

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector | Network (N) | Exploited remotely via API call |
| Attack Complexity | Low (L) | Single API call |
| Privileges Required | Low (L) | Requires any authenticated user account |
| User Interaction | None (N) | No victim interaction required |
| Scope | Unchanged (U) | Impact within the knowledge base boundary |
| Confidentiality | Low (L) | Discloses KB metadata (IDs, names, descriptions) across all users |
| Integrity | None (N) | No direct data modification |
| Availability | None (N) | No denial of service |

## Attack Scenario

1. Attacker (any authenticated user) sends:
   ```
   POST /api/v1/retrieval/query/doc
   {
     "collection_name": "knowledge-bases",
     "query": "confidential"
   }
   ```
2. `_validate_collection_access` does not recognize the `knowledge-bases` prefix and lets the request pass.
3. The vector search returns the most relevant documents from the meta-collection — knowledge base records including their UUIDs, names, and descriptions — across all users on the instance.
4. Attacker varies the query to enumerate more KBs: `"project"`, `"internal"`, `"private"`, etc.
5. Attacker now has a full target list for subsequent attacks (destruction, poisoning, content extraction).

## Impact

- **Information disclosure:** KB names and descriptions may reveal sensitive project names, internal initiatives, or user activities
- **Enabler for other attacks:** Unlocks the following findings by supplying the required target UUIDs:
  - KB destruction/poisoning via `process/web`
  - Cross-user content injection via `process/file`
  - RAG vector search access bypass in `retrieval/utils.py`
- Transforms these from theoretical (requires UUID guessing) to trivially exploitable (UUIDs enumerable)

## Preconditions

- Attacker must have a valid user account

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-6c2x-gcp3-gp73
- https://nvd.nist.gov/vuln/detail/CVE-2026-44557
- https://github.com/open-webui/open-webui
