# [H] p4 vulnerable to Command Injection due to improper input sanitization

## Summary
Severity: High
Advisory: GHSA-jfm8-hwhg-r6gg
CVE: CVE-2022-25171
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-20
Source: https://github.com/advisories/GHSA-jfm8-hwhg-r6gg
Type: github-advisory

## Affected
- npm: `p4` — affected >=0 <0.0.7

## Details
The package p4 before 0.0.7 is vulnerable to Command Injection via the run() function due to improper input sanitization

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25171
- https://github.com/natelong/p4/commit/ae42e251beabf67c00539ec0e1d7aa149ca445fb
- https://github.com/natelong/p4
- https://github.com/natelong/p4/blob/master/p4.js#23L12
- https://security.snyk.io/vuln/SNYK-JS-P4-3167330
