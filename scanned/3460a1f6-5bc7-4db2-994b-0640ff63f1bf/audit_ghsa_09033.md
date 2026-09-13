# [M] Open WebUI's Channel Access Grants Bypass filter_allowed_access_grants

## Summary
Severity: Medium
Advisory: GHSA-7rjh-px4v-5w55
CVE: CVE-2026-44558
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-7rjh-px4v-5w55
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Channel Access Grants Bypass filter_allowed_access_grants

## Affected Component

Channel creation and update endpoints:
- `backend/open_webui/routers/channels.py` (lines 291-340, `create_new_channel`)
- `backend/open_webui/routers/channels.py` (lines 617-638, `update_channel_by_id`)
- `backend/open_webui/models/channels.py` (lines 825-826, `set_access_grants` call without filtering)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions supporting user-created group channels with access grants.

## Description

All resource routers in Open WebUI (knowledge, models, notes, prompts, tools, skills) call `filter_allowed_access_grants()` before persisting access grants. This function strips `principal_id: "*"` wildcard grants from users who lack the relevant `sharing.public_*` permission, and strips individual user grants from users who lack `access_grants.allow_users` permission.

The channel router does not call `filter_allowed_access_grants` on either create or update paths. A non-admin user who can create group channels (or who owns a channel) can submit arbitrary access grants — including public wildcard grants — and those grants are stored verbatim, bypassing the admin's permission framework.

```python
# channels.py — access_grants from form data flow directly into persistence
# No call to filter_allowed_access_grants() anywhere in these paths.

# Compare with knowledge.py / models.py / notes.py / prompts.py / tools.py / skills.py,
# all of which do:
#     form_data.access_grants = filter_allowed_access_grants(user, form_data.access_grants)
# before creating or updating.
```

## Attack Scenario

1. Admin configures permissions so that regular users do NOT have `sharing.public_channels` — public sharing of channels is intended to be admin-only.
2. Attacker (a regular user) creates or owns a group channel.
3. Attacker sends:
   ```
   POST /api/v1/channels/
   {
     "name": "public-channel",
     "type": "group",
     "access_control": {
       "access_grants": [
         {"principal_type": "user", "principal_id": "*", "permission": "read"}
       ]
     }
   }
   ```
4. `set_access_grants` is called directly without `filter_allowed_access_grants` — the wildcard grant is persisted.
5. The channel becomes publicly readable to every user on the instance, despite the admin's policy prohibiting public channels for regular users.

The same attack works via `POST /api/v1/channels/{id}/update` for any channel the attacker owns.

## Impact

- Regular users can bypass the `sharing.public_channels` permission and make channels publicly accessible
- Regular users can bypass `access_grants.allow_users` to grant individual-user access in environments where only group-based sharing is intended
- Admin's permission framework for channels is silently ineffective
- Creates an inconsistency with every other resource type in the codebase, making the security posture harder to reason about

## Preconditions

- Attacker must have an account with the ability to create group channels (default user capability), or ownership of an existing channel
- Admin must have configured restrictive sharing permissions for regular users (otherwise there's no policy to bypass)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-7rjh-px4v-5w55
- https://nvd.nist.gov/vuln/detail/CVE-2026-44558
- https://github.com/open-webui/open-webui
