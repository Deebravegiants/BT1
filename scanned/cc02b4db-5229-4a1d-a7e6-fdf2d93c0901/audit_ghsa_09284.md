# [H] Open WebUI: Stale Admin Role in Socket.IO Session Pool Enables Post-Demotion Cross-User Note Access

## Summary
Severity: High
Advisory: GHSA-45m8-cpm2-3v65
CVE: CVE-2026-44553
CWE: CWE-384, CWE-613, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-45m8-cpm2-3v65
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Stale Admin Role in Socket.IO Session Pool Enables Post-Demotion Cross-User Note Access

## Affected Component

Socket.IO session state and role-check callsites:
- `backend/open_webui/socket/main.py` (lines 330-351, `connect` handler — role snapshotted into SESSION_POOL)
- `backend/open_webui/socket/main.py` (lines 393-398, `heartbeat` handler — does not refresh role)
- `backend/open_webui/socket/main.py` (line 538, `ydoc:document:join` — uses cached role for admin check)
- `backend/open_webui/socket/main.py` (line 611, `document_save_handler` — uses cached role for admin check)
- `backend/open_webui/routers/users.py` (lines 557-633, role update — does not invalidate SESSION_POOL)
- `backend/open_webui/routers/users.py` (line 641, user delete — does not invalidate SESSION_POOL)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with the collaborative document (Yjs) Socket.IO handlers.

## Description

When a user connects via Socket.IO, the `connect` handler authenticates them via JWT and stores their user record (including `role`) in the in-memory `SESSION_POOL` dictionary keyed by session ID. The `heartbeat` handler keeps the session alive indefinitely but only refreshes the `last_seen_at` timestamp — never the role.

Role checks in the Yjs collaborative document handlers (`ydoc:document:join`, `document_save_handler`) consult the cached `SESSION_POOL` role rather than the database. Meanwhile, administrative role changes and user deletions do not iterate `SESSION_POOL` to disconnect affected sessions. As a result, a user whose admin role has been revoked retains admin privileges within their existing Socket.IO session for as long as they keep the connection alive (via automatic heartbeats).

HTTP endpoints are not affected — `get_current_user` at [utils/auth.py](backend/open_webui/utils/auth.py) refetches the user record from the database on every request. The gap is exclusive to the Socket.IO session cache.

```python
# socket/main.py:330-351 — role snapshotted at connect time
async def connect(sid, environ, auth):
    user = None
    if auth and 'token' in auth:
        data = decode_token(auth['token'])
        if data is not None and 'id' in data:
            user = Users.get_user_by_id(data['id'])
        if user:
            SESSION_POOL[sid] = {
                'id': user.id,
                'role': user.role,   # ← snapshotted, never refreshed
                ...
            }

# socket/main.py:393-398 — heartbeat refreshes last_seen_at only
async def heartbeat(sid, data):
    user = SESSION_POOL.get(sid)
    if user:
        SESSION_POOL[sid] = {**user, 'last_seen_at': int(time.time())}
        # role is carried forward unchanged

# socket/main.py:538 — admin check against cached role
if user.get('role') != 'admin' and not has_access(user_id, 'note', note_id, 'read', db=db):
    return
```

## Attack Scenario

1. User B is an admin and has an active browser session with a live Socket.IO connection. `SESSION_POOL[sid]` records `role='admin'`.
2. Admin A demotes User B to a regular user via `POST /api/v1/users/{B_id}/update`. The DB `user.role` becomes `'user'`.
3. No Socket.IO disconnect, no SESSION_POOL update, no token revocation event is triggered by the role change.
4. User B's client continues sending `heartbeat` events every few seconds; these are accepted and only refresh `last_seen_at`.
5. User B emits `ydoc:document:join` with `document_id = 'note:<victim_note_id>'` for any note they do not own.
6. The handler at line 538 evaluates `user.get('role') != 'admin'` — returns `False` because `SESSION_POOL` still holds the stale `admin` role. Access check is bypassed, User B joins the document room, receives full document state and live updates.
7. User B emits `ydoc:document:update` for the same note. The handler at line 611 performs the same cached-admin check, bypasses authorization, and persists attacker-controlled content to the victim's note via `Notes.update_note_by_id`.

The same bypass occurs if the user is deleted entirely (`delete_user_by_id`) — the deleted user retains admin privileges on their live socket until disconnection.

## Impact

- Read access to any user's notes after admin privileges have been revoked
- Write access (content injection, overwrite) to any user's notes under the same conditions
- The stale privilege is bounded only by the attacker's willingness to keep the Socket.IO connection alive; heartbeats extend the session indefinitely
- Official admin demotion or user deletion gives a false sense of security — HTTP access is correctly revoked, but real-time collaborative access silently continues

## Preconditions

- Attacker must have an active Socket.IO connection established while they held admin role
- Attacker must retain the Socket.IO session after demotion/deletion (trivial — just don't close the browser)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-45m8-cpm2-3v65
- https://nvd.nist.gov/vuln/detail/CVE-2026-44553
- https://github.com/open-webui/open-webui
