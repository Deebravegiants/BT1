# [M] Cross-site scripting in PageKit

## Summary
Severity: Medium
Advisory: GHSA-mrwr-2945-fr22
CVE: CVE-2021-32245
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-mrwr-2945-fr22
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
In PageKit v1.0.18, a user can upload SVG files in the file upload portion of the CMS. These SVG files can contain malicious scripts. This file will be uploaded to the system and it will not be stripped or filtered. The user can create a link on the website pointing to "/storage/exp.svg" that will point to http://localhost/pagekit/storage/exp.svg. When a user comes along to click that link, it will trigger a XSS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32245
- https://github.com/pagekit/pagekit/issues/963
