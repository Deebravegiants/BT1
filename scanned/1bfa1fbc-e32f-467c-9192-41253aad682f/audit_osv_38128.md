# [M] Bulwark Webmail: Information Exposure: password returned in /api/auth/session

## Summary
Severity: Medium
Advisory: CVE-2026-34833
Aliases: GHSA-47pm-883h-885r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34833
Type: osv

## Details
Bulwark Webmail is a self-hosted webmail client for Stalwart Mail Server. Prior to version 1.4.10, the GET /api/auth/session endpoint previously included the user's plaintext password in the JSON response. This exposed credentials to browser logs, local caches, and network proxie. This issue has been patched in version 1.4.10.

## References
- https://github.com/bulwarkmail/webmail/releases/tag/1.4.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34833.json
- https://github.com/bulwarkmail/webmail/security/advisories/GHSA-47pm-883h-885r
- https://nvd.nist.gov/vuln/detail/CVE-2026-34833
