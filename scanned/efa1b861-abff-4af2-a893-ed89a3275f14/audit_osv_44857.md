# [M] Open WebUI: A user's session cookies are sent to tool servers configured for bearer authentication

## Summary
Severity: Medium
Advisory: CVE-2026-87015
Aliases: GHSA-p78m-89r6-pgf7
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87015
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.6.27 until 0.11.1, backend/open_webui/utils/tools.py captured a cookie jar from the enclosing connection loop instead of binding it to each external tool callable. When multiple tool servers were attached and a session or system OAuth connection was processed last, a request to a different server configured for bearer authentication could include the calling user's Open WebUI session cookies, allowing that server's operator to reuse the session and take over the account. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87015.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-p78m-89r6-pgf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-87015
- https://github.com/open-webui/open-webui/commit/cd9db21c5276807a2975ddba17cef369ad1114b7
- https://github.com/open-webui/open-webui/pull/28630
