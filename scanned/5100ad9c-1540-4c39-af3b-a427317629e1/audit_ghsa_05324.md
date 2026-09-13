# [H] Crawl4AI: Unauthenticated SSRF on the Docker server streaming crawl path (/crawl/stream)

## Summary
Severity: High
Advisory: GHSA-wm69-2pc3-rmmf
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-wm69-2pc3-rmmf
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.9.0

## Details
### Summary

The Docker API server applied its SSRF destination check (`validate_url_destination`) on the non-streaming `/crawl` path but not on the streaming path. `handle_stream_crawl_request` passed seed URLs straight to the crawler with no destination validation. A remote, unauthenticated client could call `POST /crawl/stream` (or `POST /crawl` with `crawler_config.stream=true`, which short-circuits to the same handler) with a URL pointing at an internal, private, or link-local address; the server fetched it and streamed the response body back. The Docker API is unauthenticated by default.

### Affected paths

`POST /crawl/stream`, and `POST /crawl` with `crawler_config.stream=true` (both route to `handle_stream_crawl_request`, `deploy/docker/api.py`).

### Impact

Unauthenticated read server-side request forgery: an attacker reads internal-only services and cloud-metadata endpoints (e.g. `http://169.254.169.254/` for IAM credentials), with the response body streamed back. This is the same class and severity as the project's prior "SSRF via Direct Crawl Endpoints" advisory; `/crawl/stream` is part of that endpoint family and was never covered by the destination check.

### Fix

`handle_stream_crawl_request` now validates every seed URL's destination with the same global-routability check as `handle_crawl_request`, before any fetch. The SSRF regression test was hardened to assert per-handler coverage (including the streaming handler) rather than a bare occurrence count, which previously let this gap pass.

### Workarounds

- Upgrade to the patched version (0.9.0).
- Enable authentication and restrict who can reach the API (note: this does not constrain which URL the API fetches).
- Restrict the container's outbound network access (egress firewall / no metadata route).

### Credits

KOH Jun Sheng - reported the streaming-path SSRF with a runnable PoC and noted the count-based regression test that masked it, plus the shared root cause with redirect/deep-crawl link following.

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-wm69-2pc3-rmmf
- https://github.com/unclecode/crawl4ai
