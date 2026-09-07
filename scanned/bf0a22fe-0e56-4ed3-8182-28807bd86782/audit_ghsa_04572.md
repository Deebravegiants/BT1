# [M] nebula-mesh: Newly-minted operator API key exposed in redirect URL (Referer, history, proxy logs)

## Summary
Severity: Medium
Advisory: GHSA-9pg3-25fq-p6cc
CVE: CVE-2026-47768
CWE: CWE-116, CWE-532, CWE-598
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-9pg3-25fq-p6cc
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.2

## Details
`internal/web/operators.go:251` — after `handleOperatorCreateAPIKey` mints a fresh 32-byte bearer token, the redirect points the operator's browser at:

    /ui/operators/<id>?new_key=<raw-token>&key_name=<name>

The raw API key ends up:
- in the browser's URL history
- in the `Referer` header on every cross-origin asset the detail page loads (any third-party SVG/CSS/JS resource the layout pulls in)
- in any reverse-proxy or load-balancer access log on the path (nginx default `combined` log captures the query string)
- in any structured log sink the operator's local browser-history backup tool ships out

`Authorization: Bearer <token>` headers go through the same hops without these problems because access logs typically don't capture request headers and the browser doesn't replay headers cross-origin.

Same handler also appends `name` (`r.FormValue("name")`) to the query string without `url.QueryEscape`, so an `&` in the operator-supplied key name corrupts query parsing and a `\r\n` in older proxies could split response headers.

## Affected
All released versions up to v0.3.1.

## Reproducer
As admin, create an API key via `/ui/operators/<id>/api-keys` (form POST). The 303 Location header carries the raw token in the query string. Open browser DevTools → Network → response headers; or check the reverse-proxy access log; or check the operator-detail page's `Referer`-emitting fetches.

## Suggested fix
Stash the raw key in a one-shot server-side flash storage (e.g., a row in `operator_sessions` keyed by session token, with a `one_shot_token` column and `consumed_at`) or in a short-lived signed cookie. Render the key once inline on the detail page after the redirect, and clear the storage on render. Pattern mirrors the recovery-codes display in the TOTP flow.

If the flash-storage refactor is too invasive, the minimal fix is to render the key inline via a `POST` → `200 OK with HTML` (no redirect), losing the post-redirect-get idiom but eliminating the URL exposure.

Also fix `name` query encoding with `url.QueryEscape` regardless of which fix shape lands.

## CVSS estimate
AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N — 5.5 (medium). AV:L because realistic exploit requires log-read access on shared infrastructure (proxy, CDN, browser-history backup) the operator's session touches.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-9pg3-25fq-p6cc
- https://github.com/juev/nebula-mesh
