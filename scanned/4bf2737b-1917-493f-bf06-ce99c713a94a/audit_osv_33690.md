# [M] application-urlshortener users can create arbitrary pages as long as they have view access to them

## Summary
Severity: Medium
Advisory: CVE-2025-48885
Aliases: GHSA-c57g-9v2r-w8v3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-48885
Type: osv

## Details
application-urlshortener create shortened URLs for XWiki pages. Versions prior to 1.2.4 are vulnerable to users with view access being able to create arbitrary pages. Any user (even guests) can create these docs, even if they don't exist already. This can enable guest users to denature the structure of wiki pages, by creating 1000's of pages with random name, that then become very difficult to handle by admins. Version 1.2.4 fixes the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48885.json
- https://github.com/xwikisas/application-urlshortener/security/advisories/GHSA-c57g-9v2r-w8v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-48885
- https://github.com/xwikisas/application-urlshortener/commit/f121a9c973fd25948e82efcb6289d53fe00a9e7d
