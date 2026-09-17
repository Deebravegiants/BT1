# [M] word-wrap vulnerable to Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-j8xg-fqg3-53r7
CVE: CVE-2023-26115
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-j8xg-fqg3-53r7
Type: github-advisory

## Affected
- npm: `word-wrap` — affected >=0 <1.2.4

## Details
All versions of the package word-wrap are vulnerable to Regular Expression Denial of Service (ReDoS) due to the usage of an insecure regular expression within the result variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26115
- https://github.com/jonschlinkert/word-wrap/commit/420dce9a2412b21881202b73a3c34f0edc53cb2e
- https://github.com/jonschlinkert/word-wrap
- https://github.com/jonschlinkert/word-wrap/blob/master/index.js#L39
- https://github.com/jonschlinkert/word-wrap/blob/master/index.js%23L39
- https://github.com/jonschlinkert/word-wrap/releases/tag/1.2.4
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-4058657
- https://security.snyk.io/vuln/SNYK-JS-WORDWRAP-3149973
