# [M] Open WebUI: POST /api/v1/images/edit bypasses the global image-edit switch and the per-user image-generation permission

## Summary
Severity: Medium
Advisory: GHSA-rqj7-6wrp-6g2g
CVE: CVE-2026-59227
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-rqj7-6wrp-6g2g
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.8.11 <0.10.0

## Details
## Summary

`POST /api/v1/images/edit` performed no authorization beyond requiring a verified account. Every other image-editing surface in Open WebUI enforces the global image-edit switch and the per-user image-generation permission — the `/api/v1/images/generations` route, the built-in `edit_image` tool, and the chat image-edit middleware — but the direct edit route enforced neither. A verified non-admin user could therefore invoke server-side image editing, reaching the configured image-edit provider with the administrator's credentials, even when the administrator had globally disabled image editing (`ENABLE_IMAGE_EDIT=False`) or denied that user image-generation permission. The image-editing UI is surfaced only to administrators (Playground), so the route additionally exposed an admin-only capability to any verified user.

## Impact

An authenticated, non-admin user can:

- bypass the global `ENABLE_IMAGE_EDIT=False` administrator control;
- bypass a denied per-user/group `features.image_generation` permission;
- cause the server to send billable image-edit requests to the configured provider (OpenAI-compatible, Gemini, or ComfyUI) using administrator-configured credentials (`IMAGES_EDIT_OPENAI_API_KEY` for the OpenAI engine).

No cross-user data is exposed and the provider credentials are never returned to the caller; the impact is the control/permission bypass and the associated billable resource consumption.

## Affected Versions

`>= 0.8.11, < 0.10.0` (the `/api/v1/images/edit` route was introduced in 0.8.11 and was ungated from the outset). Fixed in **v0.10.0**.

## Details

`/api/v1/images/generations` enforces `ENABLE_IMAGE_GENERATION` (403 if globally disabled) and `features.image_generation` (403 for non-admins without the permission). The `edit_image` built-in tool and the chat image-edit middleware likewise gate on `ENABLE_IMAGE_EDIT` and `features.image_generation`. The direct `POST /api/v1/images/edit` route ran on `Depends(get_verified_user)` alone and proceeded straight to provider dispatch, applying none of these controls.

## Proof of Concept

As a verified non-admin user, with image editing globally disabled (`ENABLE_IMAGE_EDIT=False`) or `features.image_generation` denied for the user:

```http
POST /api/v1/images/edit
Authorization: Bearer <non_admin_user_token>
Content-Type: application/json

{"image":"data:image/png;base64,<png>","prompt":"edit","model":"gpt-image-1"}
```

The request reaches the configured image-edit provider and returns an edited image despite the disabled control/permission.

## Patch

The direct route is split from its shared implementation (mirroring `generate_images`/`image_generations`): a thin `/edit` route now enforces `ENABLE_IMAGE_EDIT` and the per-user `features.image_generation` permission before delegating to the shared `image_edits()` implementation. The internal callers (the `edit_image` tool and the chat middleware) call the implementation directly and already gate themselves, so they are unaffected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-rqj7-6wrp-6g2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-59227
- https://github.com/open-webui/open-webui/pull/26009
- https://github.com/open-webui/open-webui/commit/e038bab66dec8d17212eec35b5cb6d6b785a4200
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
