# [H] Open WebUI: SSRF into internal services via unvalidated sub-resource requests in the Playwright web loader

## Summary
Severity: High
Advisory: GHSA-w2rx-84hp-gg95
CVE: CVE-2026-70479
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-w2rx-84hp-gg95
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.6 <0.11.0

## Details
## Summary
With the Playwright web loader enabled, Open WebUI opens user-submitted URLs in a real browser and validates the destination address before allowing the request. That check only ran for the top-level page request. Every other request the page issued was passed through unvalidated, so a page could use its own JavaScript to reach addresses the validation exists to block. Because the loader returns the page's final DOM to the requesting user, anything the page read back from those addresses ends up in the web-search or RAG output.

## Preconditions
- `WEB_LOADER_ENGINE=playwright`. This is not the default; deployments on the default web loader are unaffected.
- A reachable Playwright browser, either local or via `PLAYWRIGHT_WS_URL`.
- Any authenticated user who can submit a URL for ingestion or trigger a web search. No administrator role is required.
- Something worth reading on a network the browser can reach. A deployment whose browser container has no route to internal services loses nothing here.

## Impact
An authenticated user can read HTTP responses from services reachable by the browser process: cloud instance metadata, other containers on the same network, and internal APIs bound to private addresses. The content is returned to the user through the normal web-search or document-ingestion result, so this is a read primitive, not a blind one. It confers no write access and no availability impact, and it does not extend beyond what the browser's network position already allows.

## Fix
Fixed in 0.11.0 by commit `bef63a2ae`. Every intercepted request is now validated, fetched with redirects disabled, re-validated on each redirect hop and then fulfilled, so neither a sub-resource nor a redirect can land on a non-global address. The same change blocks the two paths that never reached the interceptor at all: service-worker requests, via `service_workers="block"`, and WebSocket connections, via a route handler that never connects upstream. Upgrading to 0.11.0 fully resolves the issue; no configuration change is required.

## Root cause
Affected component: `SafePlaywrightURLLoader` in `backend/open_webui/retrieval/web/utils.py`, in both the sync and async request interceptors. Affected setup: only builds running the Playwright loader engine.

The interceptor was written to guard navigation, and its first action was to return early for any request whose resource type was not `document`. The intent was that only the page the user asked for needs address validation, but a browser page is not a single request: once the validated document loads, its scripts issue further requests under the page's own control, and those never reached the validation. The address check was therefore applied to the one request the attacker did not need to control, and skipped on every request they did.

## Proof of concept
Reported against 0.10.2 by driving the interceptor directly with stand-in route and request objects, one call per resource type, against `http://169.254.169.254/latest/meta-data/`. The `document` type is aborted; every other type is continued unvalidated. The browser and the network request were seeded rather than driven end to end; the code path exercised is the one the browser reaches for each sub-resource.

## Credits
- **@edwardav970** — identified that address validation was applied only to the top-level document request, leaving every sub-resource type unvalidated.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-w2rx-84hp-gg95
- https://github.com/open-webui/open-webui/pull/27526
- https://github.com/open-webui/open-webui/commit/bef63a2ae915571d50d2722a635e8bfa753d7877
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
