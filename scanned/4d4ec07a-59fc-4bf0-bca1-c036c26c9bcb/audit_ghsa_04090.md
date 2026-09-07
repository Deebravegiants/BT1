# [M] Moderate severity vulnerability that affects total.js

## Summary
Severity: Medium
Advisory: GHSA-72p5-2r6g-fm6v
CVE: CVE-2019-10260
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-02
Source: https://github.com/advisories/GHSA-72p5-2r6g-fm6v
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.3.0-13

## Details
Total.js CMS 12.0.0 has XSS related to themes/admin/views/index.html (item.message) and themes/admin/public/ui.js (column.format).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10260
- https://github.com/totaljs/cms/commit/75205f93009db3cf8c0b0f4f1fc8ab82d70da8ad
- https://github.com/totaljs/cms/commit/8b9d7dada998c08d172481d9f0fc0397c4b3c78d
- https://github.com/advisories/GHSA-72p5-2r6g-fm6v
