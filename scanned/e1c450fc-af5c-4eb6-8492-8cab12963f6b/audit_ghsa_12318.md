# [H] Regular Expression Denial of Service in is-my-json-valid

## Summary
Severity: High
Advisory: GHSA-f522-ffg8-j8r6
CVE: CVE-2016-2537
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-f522-ffg8-j8r6
Type: github-advisory

## Affected
- npm: `is-my-json-valid` — affected >=0 <2.12.4

## Details
Version of `is-my-json-valid` before 2.12.4 are vulnerable to regular expression denial of service (ReDoS) via the email validation function.


## Recommendation

Update to version 2.12.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2537
- https://github.com/github/advisory-database/pull/4850
- https://github.com/mafintosh/is-my-json-valid/pull/159
- https://github.com/mafintosh/is-my-json-valid/commit/b3051b277f7caa08cd2edc6f74f50aeda65d2976
- https://github.com/mafintosh/is-my-json-valid/commit/eca4beb21e61877d76fdf6bea771f72f39544d9b
- https://hackerone.com/reports/317548
- https://github.com/advisories/GHSA-f522-ffg8-j8r6
- https://github.com/mafintosh/is-my-json-valid
- https://www.npmjs.com/advisories/572
- https://www.npmjs.com/advisories/76
