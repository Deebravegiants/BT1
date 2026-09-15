# [M] Open WebUI: DNS Rebinding SSRF Bypass

## Summary
Severity: Medium
Advisory: GHSA-h6x2-583h-x99r
CVE: CVE-2026-54020
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-h6x2-583h-x99r
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.11.0

## Details
## Summary
Open WebUI vetted user-supplied URLs by resolving the hostname once and rejecting private, loopback and link-local addresses, then let the HTTP client resolve that hostname again at connect time. An attacker who controls the authoritative DNS for a hostname they submit can answer with a public address during the check and an internal one at connect, so the fetch reaches an address the check was meant to block. Every user-reachable fetch gated by that check was affected, and most of them hand the internal response back to the attacker.

## Preconditions
- An account on the instance. No admin rights and no non-default configuration.
- Control of the authoritative DNS for a hostname the attacker submits, serving a TTL of 0 and alternating answers.
- One of the affected entry points: URL ingest for retrieval, an `image_url` in a chat completion, image editing, or the OAuth profile-picture fetch.
- The OAuth path additionally needs OAuth login configured and a picture claim (`OAUTH_PICTURE_CLAIM`, default `picture`) the user can influence, which is the case on self-service OIDC providers and providers with a user-editable avatar URL. On an existing account it also needs `OAUTH_UPDATE_PICTURE_ON_LOGIN`, which is off by default. Deployments without OAuth are not affected on that path; the other paths need no configuration at all.

## Impact
The server can be made to issue requests to addresses only it can reach: cloud instance metadata such as 169.254.169.254, loopback-bound admin APIs, and internal network services. The response comes back to the attacker on most paths, as document content on the retrieval path, described by the vision model on the chat image path, and base64-encoded into the profile picture on the OAuth path; the image-edit path is blind. On the OAuth path the server also forwards the OAuth access token as a Bearer header to the fetched URL, so a rebind hands that token to the internal target. On a cloud host with IMDSv1 reachable this is enough to take instance IAM credentials.

Exploitation depends on winning the gap between the two resolutions, which the attacker influences but does not fully control. Admin-configured image-generation backends and the shared session pool are not affected and deliberately keep the default client, since an administrator may legitimately point those at an internal host.

## Fix
Fixed in v0.11.0 (#24759, #25775, #25960, #26699). The check now happens at the connection layer instead of ahead of it: a `requests` transport adapter resolves the hostname once and connects to that same validated address, and an aiohttp resolver applies the same global-IP check, exposed as a one-off session used by every fetch behind the URL check. Upgrading to v0.11.0 resolves this with no configuration change.

## Root cause
Affected components:
- retrieval web loader (`SafeWebBaseLoader`)
- retrieval content probe (`get_content_from_url`)
- chat image fetch (`get_image_base64_from_url`)
- image edit fetch (`load_url_image`)
- OAuth profile-picture fetch (`_process_picture_url`)

The URL check resolved the hostname and inspected the resulting IP, but nothing tied that decision to the connection that followed: the HTTP client resolved the name again on its own, and the second answer was never inspected. The check was therefore an opinion about a past lookup rather than a constraint on the actual connection, which is what a rebinding DNS server defeats. The first connection-layer guard covered only the retrieval loader, leaving the sibling probe, image and OAuth fetches on default clients until each was reported in turn.

## Credits
- @rezaduty — the rebinding time-of-check/time-of-use bypass and the retrieval loader path.
- @nikchillz — the retrieval content-probe path.
- @dhyabi2 — the chat `image_url` path, where the internal response is read back through the vision model.
- @geo-chen — the image-edit path.
- @bogdancherniy11-sudo — the OAuth profile-picture path, where the rebind also discloses the forwarded OAuth access token.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-h6x2-583h-x99r
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
