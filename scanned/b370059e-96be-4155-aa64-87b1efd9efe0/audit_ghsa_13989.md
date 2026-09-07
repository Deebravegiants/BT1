# [M] Craft CMS stored XSS in indexedVolumes

## Summary
Severity: Medium
Advisory: GHSA-6qjx-787v-6pxr
CVE: CVE-2023-33197
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-6qjx-787v-6pxr
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.4.6

## Details
### Summary
XSS can be triggered via the Update Asset Index utility

### PoC
1. Access setting tab
2. Create new assets
3. In assets name inject payload: "<script>alert(26)</script>
4. Click Utilities tab
5. Choose all volumes, or volume trigger xss
7. Click Update asset indexes.

XSS will be triggered

Json response volumes name makes triggers the payload

    "session":{"id":1,"indexedVolumes":{"1":"\"<script>alert(26)</script>"},

It’s run on every POST request in the utility.

Resolved in https://github.com/craftcms/cms/commit/8c2ad0bd313015b8ee42326af2848ee748f1d766

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-6qjx-787v-6pxr
- https://nvd.nist.gov/vuln/detail/CVE-2023-33197
- https://github.com/craftcms/cms/commit/8c2ad0bd313015b8ee42326af2848ee748f1d766
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.4.6
