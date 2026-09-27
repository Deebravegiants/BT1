# [M] Open WebUI Missing Access Check on Channel Members Endpoint for Standard Channels

## Summary
Severity: Medium
Advisory: GHSA-c7wp-3qh5-55pv
CVE: CVE-2026-44559
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-c7wp-3qh5-55pv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Missing Access Check on Channel Members Endpoint for Standard Channels

## Affected Component

Channel members listing endpoint:
- `backend/open_webui/routers/channels.py` (lines 445-507, `get_channel_members_by_id`)

## Affected Versions

Current main branch and likely all versions with the channels feature.

## Description

The `GET /api/v1/channels/{id}/members` endpoint only checks membership for `group` and `dm` channel types (lines 467-469). For standard channels — including private ones — there is no `channel_has_access` check before returning the member list. Any authenticated user who knows a private channel's UUID can enumerate all users with access to that channel.

```python
# Line 467-469: only group/dm channels are checked
if channel.type in ['group', 'dm']:
    if not Channels.is_user_channel_member(channel.id, user.id, db=db):
        raise HTTPException(...)
# Standard channels fall through with NO access check
```

Compare with other channel endpoints (e.g., `get_channel_messages` at line 688) which correctly call `channel_has_access(user.id, channel, permission='read')` for standard channels.

## CVSS 3.1 Breakdown

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector | Network (N) | Exploited remotely via API call |
| Attack Complexity | Low (L) | Single API call, no special conditions |
| Privileges Required | Low (L) | Requires a valid user account |
| User Interaction | None (N) | No victim interaction required |
| Scope | Unchanged (U) | Impact is within the channel authorization boundary |
| Confidentiality | Low (L) | Leaks user identities and details for a private channel |
| Integrity | None (N) | No data modification |
| Availability | None (N) | No denial of service |

## Attack Scenario

1. Attacker obtains a private standard channel's UUID (via logs, browser history, URL observation, or other API responses).
2. Attacker calls `GET /api/v1/channels/{id}/members`.
3. The server returns the full list of permitted users including their IDs, names, emails, roles, and profile images.
4. The attacker has no access to the channel's messages (those endpoints check access correctly), but now knows exactly who does.

## Impact

- Leaks the identity and personal details of every user with access to a private channel
- Reveals organizational structure and project assignments
- Enables targeted social engineering against channel members

## Preconditions

- Channels feature must be enabled (disabled by default)
- Attacker must know the channel UUID (not guessable, but obtainable through indirect means)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-c7wp-3qh5-55pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44559
- https://github.com/open-webui/open-webui
