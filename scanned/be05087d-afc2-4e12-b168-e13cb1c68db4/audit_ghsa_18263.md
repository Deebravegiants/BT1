# [M] sanitize-html is vulnerable to XSS through incomprehensive sanitization

## Summary
Severity: Medium
Advisory: GHSA-qhxp-v273-g94h
CVE: CVE-2019-25225
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-qhxp-v273-g94h
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=0 <2.0.0-beta

## Details
`sanitize-html` prior to version 2.0.0-beta is vulnerable to Cross-site Scripting (XSS). The `sanitizeHtml()` function in `index.js` does not sanitize content when using the custom `transformTags` option, which is intended to convert attribute values into text. As a result, malicious input can be transformed into executable code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25225
- https://github.com/apostrophecms/sanitize-html/issues/293
- https://github.com/apostrophecms/sanitize-html/pull/156
- https://github.com/apostrophecms/sanitize-html/commit/712cb6895825c8bb6ede71a16b42bade42abcaf3
- https://github.com/Checkmarx/Vulnerabilities-Proofs-of-Concept/tree/main/2019/CVE-2019-25225
- https://github.com/apostrophecms/sanitize-html
