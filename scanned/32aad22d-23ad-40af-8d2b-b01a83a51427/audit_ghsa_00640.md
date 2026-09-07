# [H] AWS Lambda parser is vulnerable to Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-6jqp-j69q-pm62
CVE: CVE-2018-7560
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-6jqp-j69q-pm62
Type: github-advisory

## Affected
- npm: `aws-lambda-multipart-parser` — affected >=0 <0.1.2

## Details
index.js in the aws-lambda-multipart-parser NPM package before 0.1.2 has a Regular Expression Denial of Service (ReDoS) issue via a crafted multipart/form-data boundary string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7560
- https://github.com/myshenin/aws-lambda-multipart-parser/commit/56ccb03af4dddebc2b2defb348b6558783d5757e
- https://github.com/advisories/GHSA-6jqp-j69q-pm62
- https://github.com/myshenin/aws-lambda-multipart-parser
