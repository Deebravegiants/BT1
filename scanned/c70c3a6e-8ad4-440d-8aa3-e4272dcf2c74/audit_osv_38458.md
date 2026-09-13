# [H] Postiz has Server-Side Request Forgery via Redirect Bypass in /api/public/stream

## Summary
Severity: High
Advisory: CVE-2026-40168
Aliases: GHSA-34w8-5j2v-h6ww
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40168
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to 2.21.5, the /api/public/stream endpoint is vulnerable to SSRF. Although the application validates the initially supplied URL and blocks direct private/internal hosts, it does not re-validate the final destination after HTTP redirects. As a result, an attacker can supply a public HTTPS URL that passes validation and then redirects the server-side request to an internal resource.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40168.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-34w8-5j2v-h6ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-40168
- https://github.com/gitroomhq/postiz-app/commit/30e8b777098157362769226d1b46d83ad616cb06
