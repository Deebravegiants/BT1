# [M] Craft CMS XSS in RSS widget feed

## Summary
Severity: Medium
Advisory: GHSA-qpgm-gjgf-8c2x
CVE: CVE-2023-33195
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-qpgm-gjgf-8c2x
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.3.0 <4.4.6

## Details
### Summary
A malformed RSS feed can deliver an XSS payload

### PoC
Create an RSS widget and add the domain https://blog.whitebear.vn/file/rss-xss2.rss
The XSS payload will be triggered by the title in tag `<item>`

Resolved in https://github.com/craftcms/cms/commit/b77cb3023bed4f4a37c11294c4d319ff9f598e1f

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-qpgm-gjgf-8c2x
- https://nvd.nist.gov/vuln/detail/CVE-2023-33195
- https://github.com/craftcms/cms/commit/b77cb3023bed4f4a37c11294c4d319ff9f598e1f
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.4.6
