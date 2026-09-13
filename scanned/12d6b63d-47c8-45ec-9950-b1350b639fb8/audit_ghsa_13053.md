# [H] MathJax Regular expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-v638-q856-grg8
CVE: CVE-2023-39663
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-v638-q856-grg8
Type: github-advisory

## Affected
- npm: `mathjax` — affected >=0

## Details
Mathjax up to v2.7.9 was discovered to contain two Regular expression Denial of Service (ReDoS) vulnerabilities in MathJax.js via the components pattern and markdownPattern. NOTE: the vendor disputes this because the regular expressions are not applied to user input; thus, there is no risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39663
- https://github.com/mathjax/MathJax/issues/3074
