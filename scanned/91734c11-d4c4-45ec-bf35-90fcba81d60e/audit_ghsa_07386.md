# [H] Open WebUI: Cross-channel message overwrite via chat completion API (single-model and multimodel message_ids)

## Summary
Severity: High
Advisory: GHSA-x2ff-v5v8-m75m
CVE: CVE-2026-59714
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-x2ff-v5v8-m75m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.5 <0.10.0

## Details
## Summary

Any authenticated user can overwrite the content of a message in a channel they do not belong to (including private and DM channels) by sending a chat completion request with a `channel:`-prefixed `chat_id` and a target `message_id`. The `channel:` path routes pipeline output through `_make_channel_emitter`, which writes to the `Messages` table using the caller-supplied `message_id` without binding it to the channel.

This advisory consolidates two filings of the same flaw: the original single-model form, and a multimodel `message_ids` variant that survives the partial fix shipped in v0.9.6 (see "Fix status" below).

## Details (as introduced in v0.9.5)

When a user submits a chat completion request with a `chat_id` starting with `channel:`, three authorization gaps combined in v0.9.5:

1. **Ownership check skipped** (`main.py`): the `channel:` prefix caused the entire ownership/membership verification block to be skipped, with no channel membership/write check replacing it.

```python
if not chat_id.startswith('local:') and not chat_id.startswith('channel:'):  # temporary/channel chats are not stored
    if is_new_chat:
        ...
    else:
        if not await Chats.is_chat_owner(chat_id, user.id) and user.role != 'admin':
            raise HTTPException(...)
```

2. **Message ID from user input**: `id` (and each value of the multimodel `message_ids` map) comes directly from the request body and is passed as `message_id` to the channel emitter.

3. **Unchecked database write** (`socket/main.py` `_make_channel_emitter`):

```python
async def _make_channel_emitter(request_info):
    channel_id = request_info['chat_id'].removeprefix('channel:')
    message_id = request_info['message_id']  # user-supplied
    ...
    await Messages.update_message_by_id(message_id, update_form)  # no channel/user authz
```

`Messages.update_message_by_id` performs a direct primary-key update with no `channel_id`/`user_id` validation.

## Fix (shipped in v0.10.0)

v0.9.6 added a channel gate to the `channel:` branch (PR #24725) that closed the single-model path, but it validated only the first entry of the multimodel `message_ids` map, leaving the multimodel fan-out exploitable. v0.10.0 closes the remaining gap with two layers:

1. **Request-time per-entry validation** (`backend/open_webui/main.py`): every entry of `message_ids` is validated against the target channel, not just the first; any entry whose target message does not belong to the channel in `chat_id` is rejected.
2. **Fail-closed emitter** (`backend/open_webui/socket/main.py`, `_make_channel_emitter`): before writing, it re-reads the target message and returns without writing unless `msg.channel_id` matches the channel derived from `chat_id`. A missing or mismatched message is a no-op, so a write can no longer land in a channel the caller does not target.

## PoC

Single-model (fixed in v0.9.6):

```bash
curl -X POST http://target:8080/api/chat/completions \
  -H "Authorization: Bearer $USER_JWT" -H "Content-Type: application/json" \
  -d '{
    "model": "llama3", "stream": true,
    "chat_id": "channel:any-channel-uuid-here",
    "id": "target-message-uuid-to-overwrite",
    "messages": [{"role": "user", "content": "Repeat exactly: This message has been tampered with"}]
  }'
```

Multimodel (still works on v0.9.6):

```json
POST /api/chat/completions
{
  "chat_id": "channel:<attacker_channel_id>",
  "message_ids": {
    "model-a": "<message_id_in_attacker_channel>",
    "model-b": "<victim_channel_message_id>"
  },
  "messages": [{"role": "user", "content": "..."}]
}
```

The first id passes channel scope validation; the second id is used by the per-model fan-out and overwrites the victim-channel message (with model output, or the provider-error string on a deterministic error). Even a failing model call writes error content to the target message.

## Impact

**Message integrity destruction:** an authenticated user can overwrite a message in a channel they cannot access, regardless of membership. The overwritten message retains the original author attribution while displaying attacker-chosen content (**impersonation**). Private channels, DM channels, and channels the attacker has no access to are all affected; the REST channel routes correctly return 403 for the same attacker, so the bypass is specific to the chat-completion channel pipeline.

## Affected versions

- Single-model path: introduced in commit `0037baeb2` (v0.9.5), fixed in v0.9.6 (#24725).
- Multimodel `message_ids` path: present from v0.9.6, fixed in v0.10.0.
- Consolidated Affected: `>= 0.9.5, < 0.10.0`. Patched: `>= 0.10.0`.

## Distinction from existing CVEs

CVE-2026-45385 (GHSA-wwhq-cx22-f7vv) covered IDOR in the REST endpoint `POST /channels/{id}/messages/{message_id}/update` (`routers/channels.py`); its fix (commit `f5e110f`) only touched `channels.py`. This finding uses a different code path (`POST /api/chat/completions` with `chat_id: "channel:<id>"` → `main.py` → `socket/main.py:_make_channel_emitter`), untouched by that fix.

## Suggested fix

Validate **every** value in `message_ids` against the channel (not just the first), rejecting any whose target message does not belong to the channel in `chat_id`. Additionally, make `_make_channel_emitter` fail closed: re-check that the target message's `channel_id` matches the channel before calling `Messages.update_message_by_id`, treating a missing or mismatched message as an error/no-op.

## Consolidation

Per Open WebUI's Report Handling policy this advisory consolidates independent reports of the same chat-completions channel-overwrite flaw:

- Single-model cross-channel overwrite via the `channel:` path: @sfwani (earliest filing).
- Multimodel `message_ids` fan-out variant that bypasses the v0.9.6 first-id-only gate: @DavidCarliez.

One CVE for the consolidated advisory.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-x2ff-v5v8-m75m
- https://github.com/open-webui/open-webui/commit/33e4e0dcc43afcca80f9c635d762cdc76c768ba9
- https://github.com/open-webui/open-webui/commit/ac3449cac91e62b08a7c28e54fcd044d14dea791
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
