# [M] Open WebUI: Deactivated Channel Members Retain Full Access to Group/DM Channels

## Summary
Severity: Medium
Advisory: GHSA-hmgr-67hw-j2cq
CVE: CVE-2026-44561
CWE: CWE-284, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-hmgr-67hw-j2cq
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Deactivated Channel Members Retain Full Access to Group/DM Channels

## Affected Component

Channel membership authorization check:
- `backend/open_webui/models/channels.py` (lines 663-673, `is_user_channel_member`)
- Used at 15 locations in `backend/open_webui/routers/channels.py`

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with the group/DM channel feature.

## Description

The `is_user_channel_member` function checks whether a `ChannelMember` row exists but does not check the `is_active` field. When a user is deactivated from a group or DM channel (removed by the channel owner, or leaves voluntarily), their membership row persists with `is_active=False` and `status='left'`. Because the authorization check ignores this field, the deactivated user retains full read and write access to the channel via direct API calls.

The channel correctly disappears from the deactivated user's channel list (the listing query at `get_channels_by_user_id` properly filters on `is_active`), but all 15 message-level endpoints in the router rely on `is_user_channel_member` for authorization, which does not filter on `is_active`.

```python
# models/channels.py:663 — missing is_active check
def is_user_channel_member(self, channel_id, user_id, db=None):
    membership = db.query(ChannelMember).filter(
        ChannelMember.channel_id == channel_id,
        ChannelMember.user_id == user_id,
    ).first()
    return membership is not None  # True even when is_active=False
```

Compare with `get_channel_by_id_and_user_id` (line 778) which correctly checks `ChannelMember.is_active.is_(True)`.

## CVSS 3.1 Breakdown

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector | Network (N) | Exploited remotely via API calls |
| Attack Complexity | Low (L) | No special conditions beyond knowing the channel ID (which the user had as a former member) |
| Privileges Required | Low (L) | Requires a valid user account and prior channel membership |
| User Interaction | None (N) | No victim interaction required |
| Scope | Unchanged (U) | Impact is within the same authorization boundary (the channel) |
| Confidentiality | Low (L) | Can read messages in a channel the user should no longer access |
| Integrity | Low (L) | Can post, edit, and delete messages in the channel |
| Availability | None (N) | No denial of service |

## Attack Scenario

1. User A and User B are members of a private group channel.
2. The channel owner removes User B (or User B leaves). User B's membership is set to `is_active=False, status='left'`.
3. The channel disappears from User B's UI — but User B noted the channel ID while they were a member.
4. User B calls the API directly:
   - `GET /api/v1/channels/{channel_id}/messages` — reads all messages, including those posted after deactivation
   - `POST /api/v1/channels/{channel_id}/messages/post` — posts new messages
   - `POST /api/v1/channels/{channel_id}/messages/{id}/update` — edits messages
   - `DELETE /api/v1/channels/{channel_id}/messages/{id}/delete` — deletes messages
5. All requests succeed because `is_user_channel_member` returns `True`.

## Impact

- Deactivated users can continue reading all new messages posted after their removal (confidentiality breach)
- Deactivated users can post, edit, and delete messages (integrity breach)
- The deactivation mechanism provides a false sense of security — channel owners believe removed users have lost access

## Preconditions

- Channels feature must be enabled (disabled by default)
- Attacker must have a valid user account
- Attacker must have been a member of the channel at some point (and thus knows the channel ID)

## Recommended Fix

Add `is_active` filtering to `is_user_channel_member`:

```python
def is_user_channel_member(self, channel_id, user_id, db=None):
    membership = db.query(ChannelMember).filter(
        ChannelMember.channel_id == channel_id,
        ChannelMember.user_id == user_id,
        ChannelMember.is_active.is_(True),
    ).first()
    return membership is not None
```

This aligns it with the existing `get_channel_by_id_and_user_id` method which already applies this filter correctly.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-hmgr-67hw-j2cq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44561
- https://github.com/open-webui/open-webui
