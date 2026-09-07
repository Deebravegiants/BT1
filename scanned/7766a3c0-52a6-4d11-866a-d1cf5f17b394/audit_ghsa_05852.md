# [H] atomic-agents-stack: Dashboard HTTP server path traversal allows arbitrary file read

## Summary
Severity: High
Advisory: GHSA-rm43-82j9-r4mj
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-rm43-82j9-r4mj
Type: github-advisory

## Affected
- PyPI: `atomic-agents-stack` — affected >=0 <1.1.0

## Details
The optional dashboard HTTP server (`atomic_agents/dashboard/serve.py`) builds filesystem paths directly from the request path and serves them without a containment check. It is the only per-request untrusted-path site in the codebase that does not route through `_io.safe_resolve_under`. Literal `../` segments survive `urlparse` and `Path` joining, so a request can read files outside the intended `agents_root` (including via the static branch).

**Impact:** arbitrary file read. The default bind is loopback, but `--host` is an operator-settable documented flag; binding `0.0.0.0` exposes this to the LAN. Even on loopback it is reachable via DNS-rebinding from a browser or SSRF from a co-located service.

**Affected:** `dashboard/serve.py` (`DashboardHandler.do_GET` / `_serve_file`), all versions through 1.0.0.

**Fix:** route every served path through `_io.safe_resolve_under` against the intended root and return 404 on `PathTraversalError`; reject `..`/separators early; optionally refuse a non-loopback `--host` unless an explicit auth/allow flag is set (matching `serve/_app.py`).

## References
- https://github.com/dep0we/atomic-agents-stack/security/advisories/GHSA-rm43-82j9-r4mj
- https://github.com/dep0we/atomic-agents-stack/commit/ec474f458122c5c0ca718d0df3078c8080338b2c
- https://github.com/dep0we/atomic-agents-stack
