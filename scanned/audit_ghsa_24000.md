# [H] Shopware vulnerable to SSRF

## Summary
Severity: High
Advisory: GHSA-5vmg-x99g-396q
CVE: CVE-2020-13970
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5vmg-x99g-396q
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.2.3

## Details
Shopware before 6.2.3 is vulnerable to a Server-Side Request Forgery (SSRF) in its "Mediabrowser upload by URL" feature. This allows an authenticated user to send HTTP, HTTPS, FTP, and SFTP requests on behalf of the Shopware platform server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13970
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-07-2020
- https://github.com/shopware/platform
- https://www.shopware.com/en/changelog/#6-2-3
