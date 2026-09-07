# [M] Concrete CMS stored XSS vulnerability in the "Top Navigator Bar" block

## Summary
Severity: Medium
Advisory: GHSA-998c-q8hh-h8gv
CVE: CVE-2024-8660
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-998c-q8hh-h8gv
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.3.3

## Details
Concrete CMS versions 9.0.0 through 9.3.3 are affected by a stored XSS vulnerability in the "Top Navigator Bar" block. Since the "Top Navigator Bar" output was not sufficiently sanitized, a rogue administrator could add a malicious payload that could be executed when targeted users visited the home page. This does not affect versions below 9.0.0  since they do not have the Top
Navigator Bar Block. Thanks, Chu Quoc Khanh for reporting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8660
- https://github.com/concretecms/concretecms/pull/12128
- https://github.com/concretecms/concretecms/commit/f5a01c88fb2630db96e58dcd7f52ea41e516d4e9
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/934-release-notes
- https://github.com/concretecms/concretecms
