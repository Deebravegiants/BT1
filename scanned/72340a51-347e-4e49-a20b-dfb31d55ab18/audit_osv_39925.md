# [M] TypeBot's WhatsApp status forwarding uses unvalidated user-controlled URLs, allowing SSRF from the Typebot server

## Summary
Severity: Medium
Advisory: CVE-2026-48483
Aliases: GHSA-5c92-7q58-4rgx
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48483
Type: osv

## Details
TypeBot is a chatbot builder tool. Prior to version 3.17.0, Typebot's WhatsApp status forwarding feature stores a workspace-configured webhook forwarding URL and later POSTs WhatsApp marketing/error status events to it from the server. The stored URL is only validated as a generic URL in settings, but the forwarding code uses the raw `ky` instance instead of the repository's SSRF-protected `safeKy` client. A workspace user who can configure WhatsApp settings can therefore make the Typebot server issue HTTP requests to internal services, private-network hosts, localhost, or metadata-style endpoints whenever the public WhatsApp production webhook receives a status payload that should be forwarded. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48483.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-5c92-7q58-4rgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-48483
- https://github.com/baptisteArno/typebot.io/commit/30cbc616e00efabb193c3221b36a0d417152592c
- https://github.com/baptisteArno/typebot.io/pull/2497
