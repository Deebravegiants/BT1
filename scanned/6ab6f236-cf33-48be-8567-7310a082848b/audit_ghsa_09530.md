# [H] Open WebUI has Broken Access Control for Completions API

## Summary
Severity: High
Advisory: GHSA-gfm2-xm6c-37qc
CVE: CVE-2026-45349
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-gfm2-xm6c-37qc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
### Summary
Any user `X` can continue the conversation of any other user `Y`, as long as the Chat ID of `Y` is known. User `X` does not even need to be an admin to do so. 

### Details
A user just needs to use the API endpoint: `/api/chat/completions` with their own API key (generated in OWUI) and the Chat ID of another user. **OWUI does not check to match the Chat ID with the user that created that Chat ID**. Note that both users will need access to the same model. This is especially relevant if there is a shared pipeline model between users. 

### PoC
1. Using OWUI v0.6.18
2. Sign in with any user `X`
3. Generate an API Key for user `X` using the settings
4. Create another user `Y`, and have a conversation in OWUI. Copy the Chat ID from the URL.
5. User `X` can now use the API `/api/chat/completions` and the Chat ID from step 4 to continue the conversation of user `Y`

### Impact
Large impact to any user in OWUI. People can read your conversations, and access private information if they know your Chat ID (which is in the URL of the chat). 

## Resolution

Fixed in commit [cf4218e68](https://github.com/open-webui/open-webui/commit/cf4218e688def6f11d195aeda6665ae5b5376b67), first released in **v0.9.0** (Apr 2026). The `chat_completion` handler at `backend/open_webui/main.py:1868` now explicitly verifies chat ownership via `Chats.is_chat_owner(chat_id, user.id)` for any request that targets an existing chat, and raises 404 for non-owners (admin bypass preserved per the documented threat model). New chats (no `chat_id` supplied, or freshly inserted via the `is_new_chat` branch) are unaffected. Users on `>= 0.9.0` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-gfm2-xm6c-37qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45349
- https://github.com/open-webui/open-webui/commit/cf4218e688def6f11d195aeda6665ae5b5376b67
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
