# [M] ThingsBoard vulnerable to stored cross-site scripting (XSS) vulnerability in the dashboard's Image Upload Gallery feature

## Summary
Severity: Medium
Advisory: GHSA-fpq4-r87v-g246
CVE: CVE-2025-34281
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-fpq4-r87v-g246
Type: github-advisory

## Affected
- Maven: `org.thingsboard:application` — affected >=0 <4.2.1

## Details
ThingsBoard versions < 4.2.1 contain a stored cross-site scripting (XSS) vulnerability in the dashboard's Image Upload Gallery feature. An attacker can upload an SVG file containing malicious JavaScript, which may be executed when the file is rendered in the UI. This issue results from insufficient sanitization and improper content-type validation of uploaded SVG files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34281
- https://github.com/thingsboard/thingsboard/pull/13927
- https://github.com/thingsboard/thingsboard/commit/b2ae6f92d12206ea185a2e882945a6b69234bf03
- https://advisory.checkmarx.net/advisory/CVE-2025-3261
- https://advisory.checkmarx.net/advisory/CVE-2025-34281
- https://github.com/thingsboard/thingsboard
- https://github.com/thingsboard/thingsboard/releases/tag/v4.2.1
- https://www.vulncheck.com/advisories/thingsboard-svg-image-stored-xss
