# [H] Regular Expression Denial of Service in Acorn

## Summary
Severity: High
Advisory: GHSA-6chw-6frg-f759
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-04-03
Source: https://github.com/advisories/GHSA-6chw-6frg-f759
Type: github-advisory

## Affected
- npm: `acorn` — affected >=5.5.0 <5.7.4
- npm: `acorn` — affected >=6.0.0 <6.4.1
- npm: `acorn` — affected >=7.0.0 <7.1.1

## Details
Affected versions of acorn are vulnerable to Regular Expression Denial of Service.
A regex in the form of /[x-\ud800]/u causes the parser to enter an infinite loop.
The string is not valid UTF16 which usually results in it being sanitized before reaching the parser.
If an application processes untrusted input and passes it directly to acorn,
attackers may leverage the vulnerability leading to Denial of Service.

## References
- https://github.com/acornjs/acorn/issues/929
- https://github.com/acornjs/acorn/commit/793c0e569ed1158672e3a40aeed1d8518832b802
- https://snyk.io/vuln/SNYK-JS-ACORN-559469
- https://www.npmjs.com/advisories/1488
