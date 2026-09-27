# [M] Open WebUI has Stored Cross-Site Scripting In Profile Picture

## Summary
Severity: Medium
Advisory: GHSA-6gh2-q7cp-9qf6
CVE: CVE-2026-45299
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-6gh2-q7cp-9qf6
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.0

## Details
## Summary

The `profile_image_url` field on the user profile update form accepted arbitrary `data:` URI values without MIME-type validation. Two distinct attack paths were independently demonstrated by separate reporters:

1. **`data:text/html;base64,...` in a new browser tab** (raresvis, 2025-04-17) — when a victim right-clicks a user's profile picture and chooses "Open image in new tab", the browser navigates to the data: URL and executes embedded scripts in the `data:` origin. Limited to social-engineering / redirect attacks because the script does not run in the application origin.

2. **`data:image/svg+xml;base64,...` re-served by the application origin** (Gh05t666nero, 2026-01-09) — `GET /api/v1/users/{user_id}/profile/image` decoded the base64 and returned `StreamingResponse(media_type=<user-controlled>)` extracted from the `data:` header. With `media_type=image/svg+xml` and `Content-Disposition: inline`, the SVG-embedded scripts executed in the **application origin**, enabling JWT theft from `localStorage` and full account takeover of any user — including admins — who loaded the malicious profile image URL.

Both attack paths share the same root cause (lack of MIME-type validation on `profile_image_url`) and are closed by the same fix.

## Vulnerable code (v0.7.0)

`backend/open_webui/routers/users.py` `get_user_profile_image_by_id()`:

```python
elif user.profile_image_url.startswith("data:image"):
    header, base64_data = user.profile_image_url.split(",", 1)
    image_data = base64.b64decode(base64_data)
    image_buffer = io.BytesIO(image_data)
    media_type = header.split(";")[0].lstrip("data:")  # user-controlled
    return StreamingResponse(
        image_buffer,
        media_type=media_type,
        headers={"Content-Disposition": "inline"},
    )
```

## Fix

Commit `773787c74` (2026-02-11), first contained in tag **v0.8.0**, applies the `validate_profile_image_url` field validator to every form that accepts `profile_image_url` (`UserModel`, `UpdateProfileForm`, `SignupForm` in `backend/open_webui/models/users.py` and `backend/open_webui/models/auths.py`). The validator explicitly rejects `data:image/svg+xml` and any non-image data URI, allowing only `data:image/{png,jpeg,gif,webp};base64` plus known internal paths and `http(s)://` URLs. This blocks both attack vectors at form submission time, so a malicious URL can no longer be persisted to the database.

## Credits

- **raresvis** — discovered the `data:text/html`-via-new-tab path
- **Gh05t666nero** — discovered the `data:image/svg+xml`-via-server-side path (the more severe origin-XSS vector that determined the consolidated CVSS)

Per our Report Handling policy, the cluster is consolidated into the earliest filing with credit to every reporter who demonstrated a distinct exploitation path.

## Affected / patched versions

- Affected: `< 0.8.0`
- Patched: `>= 0.8.0`

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-6gh2-q7cp-9qf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45299
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.0
