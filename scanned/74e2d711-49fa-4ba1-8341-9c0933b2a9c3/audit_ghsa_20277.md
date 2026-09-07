# [M] Cross-site Scripting in SEOmatic plugin

## Summary
Severity: Medium
Advisory: GHSA-6hjc-m38h-7jhh
CVE: CVE-2021-41750
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-13
Source: https://github.com/advisories/GHSA-6hjc-m38h-7jhh
Type: github-advisory

## Affected
- Packagist: `nystudio107/craft-seomatic` — affected >=0 <3.4.11

## Details
A cross-site scripting (XSS) vulnerability in the SEOmatic plugin 3.4.10 for Craft CMS 3 allows remote attackers to inject arbitrary web script via a GET to /index.php?action=seomatic/file/seo-file-link with url parameter containing the base64 encoded URL of a malicious web page / file and fileName parameter containing an arbitrary filename with the intended content-type to be rendered in the user's browser as the extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41750
- https://github.com/nystudio107/craft-seomatic/commit/4e46b792ce973ac0c652fb330055f41aca1981c8
- https://github.com/nystudio107/craft-seomatic/commit/5f2cdc7c39e0a4bfb60d2f84131508f0a87b2873
- https://github.com/nystudio107/craft-seomatic
- https://github.com/nystudio107/craft-seomatic/blob/develop/CHANGELOG.md
