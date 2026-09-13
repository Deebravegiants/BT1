# [H] Open WebUI: Unauthenticated requests can stall the server via uncached OIDC fetches in back-channel logout

## Summary
Severity: High
Advisory: CVE-2026-87011
Aliases: GHSA-3g9q-v48f-hh9w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87011
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.9.0 until 0.11.1, the unauthenticated POST /oauth/backchannel-logout handler in backend/open_webui/utils/oauth.py fetched the OIDC discovery document and signing keys before validating a submitted logout token. Each request repeated uncached network fetches, and the signing-key lookup blocked the async event loop, so requests carrying invalid tokens could stall the single-worker instance and amplify traffic to the identity provider when ENABLE_OAUTH_BACKCHANNEL_LOGOUT was enabled. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87011.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3g9q-v48f-hh9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-87011
- https://github.com/open-webui/open-webui/commit/aeda6ff13a25d3b3ba1b303609f35382db22142c
