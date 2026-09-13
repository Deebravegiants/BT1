# [H] node-qpdf vulnerable to command injection 

## Summary
Severity: High
Advisory: GHSA-fpr8-4wvx-j9q3
CVE: CVE-2023-26155
CWE: CWE-77, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-10-14
Source: https://github.com/advisories/GHSA-fpr8-4wvx-j9q3
Type: github-advisory

## Affected
- npm: `node-qpdf` — affected >=0

## Details
All versions of the package node-qpdf are vulnerable to Command Injection such that the package-exported method encrypt() fails to sanitize its parameter input, which later flows into a sensitive command execution API. As a result, attackers may inject malicious commands once they can specify the input pdf file path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26155
- https://github.com/nrhirani/node-qpdf/issues/23
- https://github.com/nrhirani/node-qpdf
- https://security.snyk.io/vuln/SNYK-JS-NODEQPDF-5747918
