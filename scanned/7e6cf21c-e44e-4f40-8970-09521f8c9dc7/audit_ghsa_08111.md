# [M] Khoj has an IDOR in Notion OAuth Flow that Enables Index Poisoning

## Summary
Severity: Medium
Advisory: GHSA-6whj-7qmg-86qj
CVE: CVE-2025-69207
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-6whj-7qmg-86qj
Type: github-advisory

## Affected
- PyPI: `khoj` — affected >=0

## Details
### Summary
An IDOR in the Notion OAuth callback allows an attacker to hijack any user's Notion integration by manipulating the state parameter. The callback endpoint accepts any user UUID without verifying the OAuth flow was initiated by that user, allowing attackers to replace victims' Notion configurations with their own, resulting in data poisoning and unauthorized access to the victim's Khoj search index.

This attack requires knowing the user's UUID which can be leaked through shared conversations where an AI generated image is present.

### Details
When users share conversations which contain AI generated images, the file path for the image is constructed using the user's UUID. Knowing this UUID, an attacker is able to intercept the OAuth callback for Notion and replace the `state` parameter with the other user's UUID and sync notion onto their account.

### PoC

The vulnerable line of code exists in `src/khoj/routers/notion.py` on the callback endpoint.
```python
@notion_router.get("/auth/callback")
async def notion_auth_callback(request: Request, background_tasks: BackgroundTasks):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # <-- Attacker controlled
    if not code or not state:
        return Response("Missing code or state", status_code=400)

    user: KhojUser = await aget_user_by_uuid(state)  # <-- No verification!

    await NotionConfig.objects.filter(user=user).adelete()  # <-- Deletes victim's config
    
    # ... OAuth token exchange ...
    
    access_token = final_response.get("access_token")
    await NotionConfig.objects.acreate(token=access_token, user=user)  # <-- Stores attacker's token
```

To exploit is relatively easy. Once we know the victim's UUID, we simply initiate the Notion sync process on our own account and intercept the callback, replacing the `state` parameter with the victim's UUID.

### Impact
Deletes user's existing Notion sync and replaces it with attacker-controlled Notion. Could allow for index poisoning. I'm not entirely sure what Khoj does with synced files but if it's being passed as context to an LLM then I can imagine there's potential here.

## References
- https://github.com/khoj-ai/khoj/security/advisories/GHSA-6whj-7qmg-86qj
- https://nvd.nist.gov/vuln/detail/CVE-2025-69207
- https://github.com/khoj-ai/khoj/commit/1b7ccd141d47f365edeccc57d7316cb0913d748b
- https://github.com/khoj-ai/khoj
- https://github.com/khoj-ai/khoj/releases/tag/2.0.0-beta.23
