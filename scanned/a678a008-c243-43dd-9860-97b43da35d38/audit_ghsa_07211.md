# [H] Open WebUI: Realtime endpoints accept Redis-revoked JWTs after signout/backchannel logout

## Summary
Severity: High
Advisory: GHSA-855v-hq7w-jmjw
CVE: CVE-2026-59219
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-855v-hq7w-jmjw
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.0 <0.10.0

## Details
## Summary

With Redis configured, Open WebUI supports JWT revocation: `POST /api/v1/auths/signout` (per-token `jti`) and OIDC back-channel logout (per-user `revoked_at`) record revocations in Redis, and HTTP auth (`get_current_user`) rejects revoked tokens with 401. The realtime authentication surfaces do not perform this check: Socket.IO connect / user-join / join-channels / join-note and the terminal websocket first-message auth validate tokens with `decode_token()` only (signature + expiry). A JWT revoked by sign-out or back-channel logout therefore continues to authenticate new realtime connections, even though the same token is rejected on HTTP.

## Affected component

- `backend/open_webui/socket/main.py` — Socket.IO `connect`, `user-join`, `join-channels`, `join-note`
- `backend/open_webui/routers/terminals.py` — terminal websocket first-message auth
- `backend/open_webui/utils/auth.py` — the revocation check was applied to HTTP only

## Root cause

HTTP auth enforces revocation:

```python
# utils/auth.py — get_current_user
if data.get('jti') and not await is_valid_token(request, data):
    raise HTTPException(status_code=401, detail='Invalid token')
```

Realtime auth calls `decode_token()` only, which verifies signature + expiry but never consults the Redis revocation keys (`{prefix}:auth:token:{jti}:revoked`, `{prefix}:auth:user:{id}:revoked_at`):

```python
# socket/main.py — connect / user-join / join-channels / join-note
data = decode_token(auth['token'])
# routers/terminals.py — _resolve_authenticated_connection
data = decode_token(token)
```

## Impact

A JWT revoked by user sign-out or OIDC back-channel logout still authenticates new realtime connections. A stolen token therefore retains realtime access after the victim signs out or the IdP performs back-channel logout — the very remediation for a compromised token. The token can populate `SESSION_POOL` as the victim, join their user/channel/note rooms (receiving realtime channel messages, collaborative-note updates and presence), drive socket-level collaboration as the victim, and pass terminal websocket authentication when terminal servers are configured. HTTP remains correctly protected (401), so REST data and state-changing REST endpoints are not reachable with the revoked token.

## Proof of Concept

Reporter PoC on a Redis-backed deployment (v0.9.6 and main): after `POST /api/v1/auths/signout`, HTTP returns 401 for the token while a Socket.IO user-join with the same token still authenticates, and the terminal WS reaches terminal-server lookup rather than rejecting it as `Invalid token`.

## Fix

Apply the revocation check on the realtime paths. The logic is factored into `is_token_revoked(redis, decoded)` (covering per-token `jti` and per-user `revoked_at`); the Socket.IO handlers and the terminal WS reject tokens that fail it, using the main app Redis where revocations are stored. HTTP `is_valid_token` delegates to the same helper, so HTTP behaviour is unchanged.

## Affected / Patched

- Affected: `>= 0.9.0, < 0.10.0`, and only when Redis is configured (without Redis, per-token revocation is not supported and sign-out does not invalidate JWTs by design).
- Patched: v0.10.0. The revocation check (`is_valid_token`, covering per-token `jti` and per-user `revoked_at`) is applied on Socket.IO connect / user-join / join-channels / join-note and the terminal websocket first-message auth, using the main app Redis where revocations are stored. HTTP `is_valid_token` delegates to the same logic, so HTTP behaviour is unchanged.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-855v-hq7w-jmjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-59219
- https://github.com/open-webui/open-webui/commit/33b91bd8ae8a100a5a306c91441a7d0b422c4cde
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
