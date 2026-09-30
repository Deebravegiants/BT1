# [M] CommonRegexJS Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pmvv-57rg-5g86
CVE: CVE-2020-26305
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-pmvv-57rg-5g86
Type: github-advisory

## Affected
- npm: `commonregex` — affected >=0

## Details
CommonRegexJS is a CommonRegex port for JavaScript. All available versions contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26305
- https://github.com/talyssonoc/CommonRegexJS/issues/4
- https://github.com/talyssonoc/CommonRegexJS
- https://securitylab.github.com/advisories/GHSL-2020-291-redos-CommonRegexJS
