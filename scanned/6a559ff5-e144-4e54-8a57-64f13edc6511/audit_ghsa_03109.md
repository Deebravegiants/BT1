# [H] Improper Input Validation and Code Injection in pdf-image

## Summary
Severity: High
Advisory: GHSA-rv7p-mmwq-x674
CVE: CVE-2020-8132
CWE: CWE-20, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-rv7p-mmwq-x674
Type: github-advisory

## Affected
- npm: `pdf-image` — affected >=0

## Details
Lack of input validation in pdf-image npm package version &lt;= 2.0.0 may allow an attacker to run arbitrary code if PDF file path is constructed based on untrusted user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8132
- https://hackerone.com/reports/781664
