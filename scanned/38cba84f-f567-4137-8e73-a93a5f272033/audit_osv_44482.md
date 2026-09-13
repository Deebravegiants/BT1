# [M] Admidio before 5.0.12 Authentication Bypass via RSS feeds

## Summary
Severity: Medium
Advisory: CVE-2026-82657
Aliases: GHSA-mg9h-42f8-2pmm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82657
Type: osv

## Details
Admidio before 5.0.12 fails to enforce login-only module restrictions in RSS feed endpoints for forum and announcements modules. Unauthenticated attackers can retrieve forum topics and announcements by sending GET requests to rss/forum.php or rss/announcements.php, disclosing titles, full post text, author names, and timestamps.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-mg9h-42f8-2pmm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82657.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82657
- https://www.vulncheck.com/advisories/admidio-before-5.0.12-authentication-bypass-via-rss-feeds
