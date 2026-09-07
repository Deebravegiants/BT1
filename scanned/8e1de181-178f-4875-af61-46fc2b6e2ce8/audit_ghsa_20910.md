# [H] steal vulnerable to Regular Expression Denial of Service via source and sourceWithComments

## Summary
Severity: High
Advisory: GHSA-28v4-jf82-jvj8
CVE: CVE-2022-37262
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-28v4-jf82-jvj8
Type: github-advisory

## Affected
- npm: `steal` — affected >=0

## Details
A Regular Expression Denial of Service (ReDoS) flaw was found in stealjs steal via the source and sourceWithComments variable in main.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37262
- https://github.com/stealjs/steal/issues/1531
- https://github.com/stealjs/steal
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/main.js#L3497
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/main.js#L3507
