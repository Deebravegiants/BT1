# [H] Postiz allows header mutation in middleware facilitates resulting in SSRF

## Summary
Severity: High
Advisory: CVE-2025-53641
Aliases: GHSA-48c8-25jq-m55f
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-07-11
Source: https://osv.dev/vulnerability/CVE-2025-53641
Type: osv

## Details
Postiz is an AI social media scheduling tool. From 1.45.1 to 1.62.3, the Postiz frontend application allows an attacker to inject arbitrary HTTP headers into the middleware pipeline. This flaw enables a server-side request forgery (SSRF) condition, which can be exploited to initiate unauthorized outbound requests from the server hosting the Postiz application. This vulnerability is fixed in 1.62.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53641.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-48c8-25jq-m55f
- https://nvd.nist.gov/vuln/detail/CVE-2025-53641
- https://github.com/gitroomhq/postiz-app/commit/65eca0e2f22155b43c78724ca43617ee52e42753
