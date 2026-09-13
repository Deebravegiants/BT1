# [H] Open WebUI: Terminal proxy forwards a spoofable, integrity-unbound user identity to the upstream (X-User-Id header and ws_terminal session_id query injection)

## Summary
Severity: High
Advisory: GHSA-j657-m4c4-24jq
CVE: CVE-2026-59224
CWE: CWE-287, CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-j657-m4c4-24jq
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
## Summary

The terminal proxy in `backend/open_webui/routers/terminals.py` forwards the Open WebUI user's identity to the upstream terminal server / backend coordinator as an authorization claim, with no cryptographic binding to the session that produced it. The forwarded identity is attacker-influenceable on both proxy paths:

1. **HTTP path (`proxy_terminal`)** sets `headers['X-User-Id'] = user.id`. Upstreams that trust `X-User-Id` as identity receive it unsigned, so an attacker who can reach the upstream by other means (directly, a compromised peer, SSRF) can spoof it.
2. **WebSocket path (`ws_terminal`)** is exploitable through Open WebUI itself, with no "other means" required. It interpolates the path parameter `session_id` directly into the upstream URL and then appends `?user_id=<caller>`:

   ```python
   upstream_url = f'{ws_base}/p/{policy_id}/api/terminals/{session_id}'
   upstream_url += f'?{urllib.parse.urlencode({"user_id": user.id})}'
   ```

`session_id` is neither validated nor URL-encoded (the HTTP sibling runs `_sanitize_proxy_path`; this path runs nothing). An encoded `?`/`&` smuggled through `session_id` survives Open WebUI's single decode and is re-decoded by the upstream, injecting an attacker-chosen `user_id` ahead of the appended one. Query parsing binds the first occurrence, so the backend coordinator resolves the spoofed user's terminal scope.

## Technical Details

The forwarded terminal identity is a bearer-style authorization claim with no integrity binding, and on the WebSocket path it is additionally injectable because `session_id` is concatenated into the URL without encoding or delimiter validation.

## Impact

A normal authenticated user can make the terminal proxy present another user's identity to the upstream backend coordinator. On backend coordinator-backed (`policy_id`) servers that scope terminal containers by `user_id`, this reaches another user's terminal scope; combined with a known active session ID (for example a chat-scoped session ID surfaced through a shared chat), it allows attaching to that user's live PTY. The HTTP-path variant additionally allows identity spoofing at the upstream tier for any deployment whose upstream trusts `X-User-Id`.

## Appendix: Affected code

- `backend/open_webui/routers/terminals.py` — `proxy_terminal` sets `headers['X-User-Id'] = user.id` with no signature.
- `backend/open_webui/routers/terminals.py` — `ws_terminal` builds the upstream URL from an unvalidated, unencoded `session_id` and appends `user_id` as a query parameter, allowing query injection.

## Appendix: Consolidation

Per the Report Handling policy, this consolidates independent reports of the same root cause (the forwarded terminal identity is spoofable / not integrity-bound) into the earliest filing:

- **@smoke-wolf** (earliest filing) — the `X-User-Id` HTTP-path identity is forwarded without integrity binding, spoofable where the upstream trusts the header.
- **@rexpository** — the `ws_terminal` `session_id` query-injection vector, proving the forwarded `user_id` is spoofable through the Open WebUI proxy itself, with no "reach the upstream by other means" precondition.

## Appendix: Recommended fix

- Validate and URL-encode `session_id` before building the upstream URL (`urllib.parse.quote(session_id, safe="")`; reject `?`, `#`, `&`, `/`, `%`, backslash, control characters). Build the query string with a URL builder so attacker-controlled path content cannot precede it.
- Bind the forwarded identity instead of passing a raw `user_id` / `X-User-Id`: emit a short-lived signed claim (for example HS256 over `{uid, iat, aud:server_id}` with a key shared only with the specific upstream) and verify it upstream.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-j657-m4c4-24jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-59224
- https://github.com/open-webui/open-webui/pull/26042
- https://github.com/open-webui/open-webui/commit/5f3a628a8d291bb5d33e1a0b0c89fb62a2927934
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
