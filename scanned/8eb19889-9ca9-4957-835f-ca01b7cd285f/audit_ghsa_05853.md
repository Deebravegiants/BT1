# [M] Open WebUI: Users denied the image-generation permission can still generate images via chat completions

## Summary
Severity: Medium
Advisory: GHSA-g423-grf7-98rv
CVE: CVE-2026-70484
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-g423-grf7-98rv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.7.0 <0.11.0

## Details
## Summary
An authenticated user whose `features.image_generation` permission has been revoked can still make the server generate images by sending the feature flag in a chat-completion request. The chat pipeline took the client-supplied `features` object at face value and never re-checked the permission that the direct image routes enforce, so the denial applied to the UI affordance but not to the server-side generation path.

## Preconditions
Image generation must be enabled and a provider configured by the administrator (`ENABLE_IMAGE_GENERATION` is off by default). The per-user permission defaults to granted, so only deployments where an administrator explicitly revoked it for some users are affected. On 0.10.0 and later the caller must also set `params.function_calling` to `legacy`; on 0.9.x and earlier the legacy mode was the default, so no special parameter was needed. Deployments on native function calling are unaffected, since that path checks the permission before registering the image tools.

## Impact
A user the administrator has explicitly denied image generation can consume the operator's configured provider through the chat API, spending the operator's API credits and provider quota and writing generated files to the operator's storage. Where an image is present in the conversation and image editing is enabled, the same handler reaches the image-edit provider as well. No provider credentials are exposed, and no other user's data is reachable.

## Fix
Fixed in 897d69a (#26703). The legacy chat-features block now re-checks `features.image_generation` against the caller's permissions before invoking the image handler, matching the check the direct image routes and the native function-calling path already performed.

## Root cause
The chat-completions endpoint stored the request's `features` object into request metadata, and `process_chat_payload` in the chat middleware dispatched to the image handler purely on the truthiness of that client-supplied flag. Permission enforcement lived on the two surfaces that were reached from the UI, the direct `/images/generations` and `/images/edit` routes and the native function-calling tool registration, and was simply absent on the legacy chat path. The flag was treated as a statement of user intent, which it is, rather than as an authorization decision, which the handler behind it made it.

## Credits
@DavidCarliez, for identifying that the chat pipeline honours the client-supplied image-generation feature flag without re-checking the permission.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-g423-grf7-98rv
- https://github.com/open-webui/open-webui/pull/26703
- https://github.com/open-webui/open-webui/commit/897d69a35c65f8ab54583bb9ca8dc74eab7bcd29
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
