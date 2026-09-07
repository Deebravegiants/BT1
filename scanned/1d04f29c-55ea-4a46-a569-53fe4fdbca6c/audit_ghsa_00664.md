# [M] Cross-site Scripting in dompurify

## Summary
Severity: Medium
Advisory: GHSA-63q7-h895-m982
CVE: CVE-2020-26870
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-12-18
Source: https://github.com/advisories/GHSA-63q7-h895-m982
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <2.0.17

## Details
Cure53 DOMPurify before 2.0.17 allows mutation XSS. This occurs because a serialize-parse roundtrip does not necessarily return the original DOM tree, and a namespace can change from HTML to MathML, as demonstrated by nesting of FORM elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26870
- https://github.com/cure53/DOMPurify/commit/02724b8eb048dd219d6725b05c3000936f11d62d
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/compare/2.0.16...2.0.17
- https://lists.debian.org/debian-lts-announce/2020/10/msg00029.html
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-26870
- https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass
- https://snyk.io/vuln/SNYK-JS-DOMPURIFY-1016634
- https://www.oracle.com//security-alerts/cpujul2021.html
