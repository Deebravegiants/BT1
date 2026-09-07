# [M] markdown-it-toc Cross-site Scripting due to title of generated toc and contents of header not being escaped

## Summary
Severity: Medium
Advisory: GHSA-wfvx-fx73-3rfj
CVE: CVE-2020-28455
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-wfvx-fx73-3rfj
Type: github-advisory

## Affected
- npm: `markdown-it-toc` — affected >=0

## Details
This affects all versions of package markdown-it-toc. The title of the generated toc and the contents of the header are not escaped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28455
- https://security.snyk.io/vuln/SNYK-JS-MARKDOWNITTOC-1044067
