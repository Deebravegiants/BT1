# [H] Open WebUI: Cross-user code-interpreter and tool execution via unvalidated Socket.IO event-caller session_id

## Summary
Severity: High
Advisory: GHSA-74h3-cxq7-vc5q
CVE: CVE-2026-59216
CWE: CWE-200, CWE-639, CWE-862, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-74h3-cxq7-vc5q
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
## Summary

An authenticated low-privilege user can execute arbitrary code-interpreter Python and tools inside **another** user's authenticated session. The Socket.IO event-caller (`get_event_call`) delivers `execute:python` / `execute:tool` events to a **client-supplied** `session_id` after only checking that the session is connected, never that it belongs to the requester. Combined with `ydoc:document:join`, which exposes the live socket ids of everyone in a shared note's collaboration room to any read-access participant, an attacker can target a victim's session and run attacker-chosen code/tools in the victim's browser context. When the victim is an administrator, that hijacked context reaches the admin-only Functions API, whose source is executed server-side, yielding remote code execution as the server process (root in the default container).

## Affected component

- `backend/open_webui/socket/main.py` — `get_event_call()` / `__event_caller__`
- `backend/open_webui/main.py` — chat-completion metadata (`session_id` taken from the request body)

## Root cause

The event-caller routes to a caller-controlled session id with no ownership check:

```python
# backend/open_webui/socket/main.py — get_event_call()
async def __event_caller__(event_data):
    session_id = request_info['session_id']
    if session_id not in SESSION_POOL:                 # only checks the session is connected
        return {'error': 'Client session disconnected.'}
    return await sio.call('events', {...}, to=session_id, ...)   # delivered to that sid
```

`session_id` originates from the request body and is never validated against the authenticated user:

```python
# backend/open_webui/main.py
metadata = {
    'user_id': user.id,                               # server-derived (trustworthy)
    'session_id': form_data.pop('session_id', None),  # client-controlled
    ...
}
```

`SESSION_POOL[session_id]` is the user record of whoever owns that socket. Because the caller checks only membership (`in SESSION_POOL`), a request carrying another user's `session_id` causes `execute:python` / `execute:tool` to be delivered to that other user's browser.

## Reachability

- `execute:python` / `execute:tool` are emitted from the code-interpreter and tool-call paths (`utils/middleware.py`, `tools/builtin.py`), all routed through `get_event_call`.
- The victim's live `session_id` is disclosed to any read-access participant of a shared note via `ydoc:document:join`.
- `POST /api/v1/chat/completions` requires only `get_verified_user` (the default user role). The attacker uses their own account and a model / Direct Connection they control to choose the payload.

## Impact

- **Any victim:** arbitrary code-interpreter Python and tool execution in the victim's authenticated session — the attacker acts with the victim's identity and origin (full session/account compromise).
- **Admin victim:** the hijacked admin context reaches `POST /api/v1/functions/create`, whose source is `exec()`'d server-side → remote code execution as the server process (root in the default container).

The Functions API is intended administrator code-execution; the vulnerability here is the cross-user delivery that lets an attacker drive another user's session — including an admin's — into it. The primitive is a full session compromise even against non-admin victims.

## Proof of Concept

The reporter's `exploit.py` reproduced on `ghcr.io/open-webui/open-webui:0.9.6` and a build of the `v0.9.6` tag, confirming blind server-side RCE out-of-band (callback returns `uid=0(root)`), using only a low-privilege `user` account that shared a note with an admin victim. Preconditions: code interpreter enabled; attacker shares a note with the victim; victim opens it while online; admin victim required for server RCE.

## Fix

`get_event_call` must verify the target session belongs to the requesting user before delivering, not merely that it is connected:

```python
session = SESSION_POOL.get(session_id)
if session is None or session.get('id') != request_info.get('user_id'):
    return {'error': 'Client session disconnected.'}
```

`user_id` in the request metadata is server-derived from the authenticated user, so it is trustworthy. Restricting `ydoc:document:join` so it does not disclose other participants' socket ids is recommended as defence-in-depth.

## Affected / Patched

- Affected: `< 0.10.0` (last affected release 0.9.6)
- Patched: v0.10.0. `get_event_call` now verifies the target session belongs to the requesting user before delivering (`session is None or session.get('id') != request_info.get('user_id')`), using the server-derived `user_id` from the request metadata. The recommended `ydoc:document:join` sid-disclosure restriction is defence-in-depth and independent of this fix; the ownership check closes the cross-user delivery regardless of whether the victim's sid is known.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-74h3-cxq7-vc5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59216
- https://github.com/open-webui/open-webui/pull/25763
- https://github.com/open-webui/open-webui/commit/386ac958144dbbbf0aa6e268070d72b681a318aa
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
