# [M] Cross site scripting in intelliants/subrion

## Summary
Severity: Medium
Advisory: GHSA-jvq4-cgfw-jgf4
CVE: CVE-2021-41502
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-12
Source: https://github.com/advisories/GHSA-jvq4-cgfw-jgf4
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
An issue was discovered in Subrion CMS v4.2.1 There is a stored cross-site scripting (XSS) vulnerability that can execute malicious JavaScript code by modifying the name of the uploaded image, closing the html tag, or adding the onerror attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41502
- https://github.com/intelliants/subrion/issues/885
- https://github.com/intelliants/subrion
