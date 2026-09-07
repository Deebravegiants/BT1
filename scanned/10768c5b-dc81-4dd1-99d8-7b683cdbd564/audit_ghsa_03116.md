# [M] Improper Input Validation in sanitize-html

## Summary
Severity: Medium
Advisory: GHSA-mjxr-4v3x-q3m4
CVE: CVE-2021-26540
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-mjxr-4v3x-q3m4
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=0 <2.3.2

## Details
Apostrophe Technologies sanitize-html before 2.3.2 does not properly validate the hostnames set by the "allowedIframeHostnames" option when the "allowIframeRelativeUrls" is set to true, which allows attackers to bypass hostname whitelist for iframe element, related using an src value that starts with "/\\example.com".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26540
- https://github.com/apostrophecms/sanitize-html/pull/460
- https://advisory.checkmarx.net/advisory/CX-2021-4309
- https://github.com/apostrophecms/sanitize-html/blob/main/CHANGELOG.md#232-2021-01-26
