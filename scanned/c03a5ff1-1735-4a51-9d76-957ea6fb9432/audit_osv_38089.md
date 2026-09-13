# [H] Postiz: Unauthenticated Full-Read SSRF via /public/stream Endpoint with Trivially Bypassable Extension Check

## Summary
Severity: High
Advisory: CVE-2026-34577
Aliases: GHSA-mv6h-v3jg-g539
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34577
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to version 2.21.3, the GET /public/stream endpoint in PublicController accepts a user-supplied url query parameter and proxies the full HTTP response back to the caller. The only validation is url.endsWith('mp4'), which is trivially bypassable by appending .mp4 as a query parameter value or URL fragment. The endpoint requires no authentication and has no SSRF protections, allowing an unauthenticated attacker to read responses from internal services, cloud metadata endpoints, and other network-internal resources. This issue has been patched in version 2.21.3.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34577.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-mv6h-v3jg-g539
- https://nvd.nist.gov/vuln/detail/CVE-2026-34577
