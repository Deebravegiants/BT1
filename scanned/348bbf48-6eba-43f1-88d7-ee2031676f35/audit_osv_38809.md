# [M] Postiz: TOCTOU DNS rebinding bypasses all SSRF URL validation paths

## Summary
Severity: Medium
Advisory: CVE-2026-42346
Aliases: GHSA-f7jj-p389-4w45
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42346
Type: osv

## Details
Postiz is an AI social media scheduling tool. From version 2.16.6 to before version 2.21.7, all SSRF protections added in v2.21.4–v2.21.6 share a fundamental TOCTOU (Time-of-Check-Time-of-Use) vulnerability: isSafePublicHttpsUrl() resolves DNS to validate the target IP, but subsequent fetch() calls resolve DNS independently. An attacker controlling a DNS server can exploit this gap via DNS rebinding to redirect requests to internal network addresses. This issue has been patched in version 2.21.7.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42346.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-f7jj-p389-4w45
- https://nvd.nist.gov/vuln/detail/CVE-2026-42346
- https://github.com/gitroomhq/postiz-app/commit/071143dcb01cdeb9d5d7019892f4c6ff7b19dbeb
