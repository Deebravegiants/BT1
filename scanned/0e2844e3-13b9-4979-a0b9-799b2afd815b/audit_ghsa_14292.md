# [M] Cross-site Scripting in Backdrop CMS

## Summary
Severity: Medium
Advisory: GHSA-3862-c622-v4fp
CVE: CVE-2023-31045
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-3862-c622-v4fp
Type: github-advisory

## Affected
- Packagist: `backdrop/backdrop` — affected >=0 <1.24.2

## Details
A stored Cross-site scripting (XSS) issue in Text Editors and Formats in Backdrop CMS before 1.24.2 allows remote attackers to inject arbitrary web script or HTML via the name parameter. When a user is editing any content type (e.g., page, post, or card) as an admin, the stored XSS payload is executed upon selecting a malicious text formatting option. 

NOTE: the vendor disputes the security relevance of this finding because "any administrator that can configure a text format could easily allow Full HTML anywhere."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31045
- https://github.com/backdrop/backdrop-issues/issues/6065
- https://github.com/backdrop-ops/backdrop-composer
- https://github.com/backdrop/backdrop/releases/tag/1.24.2
