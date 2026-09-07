# [M] Open WebUI: /api/v1/channels/{id}/members exposes full user model including sensitive credentials

## Summary
Severity: Medium
Advisory: GHSA-gh7p-78x6-jw6m
CVE: CVE-2026-59222
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-gh7p-78x6-jw6m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.7.0 <0.10.0

## Details
### Summary

The channel members endpoint serializes and returns **full user models** for channel participants, including settings objects. A normal user in a DM can retrieve admin-only sensitive configuration such as webhook URLs and tool server key material (`settings.ui.toolServers[].key`), which is not available via standard user info APIs.

### Details

The endpoint GET `/api/v1/channels/{id}/members` returns the full serialized user model for every member in the channel. In both the DM and non-DM code paths, the handler constructs the response with `[UserModelResponse(**user.model_dump(), is_active=...)]` and returns it as the users list. Because `UserModel` (`models/users.py`) includes a settings object (`UserSettings`) and arbitrary UI configuration (`settings.ui`), the endpoint exposes other users' sensitive configuration to any channel participant.

Practically, a regular user who participates in a DM or group can call `/api/v1/channels/{id}/members` and receive other members' settings, including admin-only details such as webhook notification URLs and tool server configuration, including credential fields like `settings.ui.toolServers[].key`. These values are not returned by the normal user profile endpoints (e.g., `/api/v1/users/{user_id}/info`).

### PoC

1. Start a local Open WebUI instance
2. Log in as admin and in the Admin Panel, go to Settings -> General and check *Channels (Beta)*, then press Save.
3. Create a low-privilege user in the Users tab
4. Click on the admin's profile bottom left, Settings and Integrations. Then click the `+` after *Manage Tool Servers* to add some tool server with a secret Bearer token (eg. `KEY`)
5. Log in as the attacker with the low-privilege account and create a new Direct Message channel with the admin user:

<img width="690" height="383" alt="image" src="https://github.com/user-attachments/assets/70208661-a0db-4457-9984-119056ca3daf" />

7. After creating, open DevTools with F12 and go to the Network tab. Then in the DM UI click on the *Users* icon top right to see the members. In the network tab, this should have triggered a `/api/v1/channels/{id}/members` request which responds with the `settings` key including `toolServers` and `key` values:

<img width="1642" height="577" alt="image" src="https://github.com/user-attachments/assets/6639d982-a156-4e8b-861e-587d86d9b152" />

The attacker has now leaked the admin's bearer token for the toolserver they configured.

### Impact

Conditions for exploit: channels are enabled and an attacker has a low-privilege account.

Webhook URLs and tool server configurations (including bearer keys) can be exfiltrated from any user.

### Original Agent Report

<img width="400" alt="app aikido dev_ai-pentests_projects_116389_assessments_019d67d4-81c8-7dd2-bb9e-0a4a774b2c78_issues_sidebarIssue=20440423 (4)" src="https://github.com/user-attachments/assets/8415553a-9f1e-4f73-929c-aa0d18a101ca" />

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-gh7p-78x6-jw6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-59222
- https://github.com/open-webui/open-webui/commit/fbcdcf146b99b5002705060a8243eee769108f9e
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
