# [H] Command Injection in puppet-facter

## Summary
Severity: High
Advisory: GHSA-g5qr-xgg7-8q2w
CVE: CVE-2022-25350
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-g5qr-xgg7-8q2w
Type: github-advisory

## Affected
- npm: `puppet-facter` — affected >=0

## Details
All versions of the package puppet-facter are vulnerable to Command Injection via the getFact function due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25350
- https://github.com/olindata/node-puppet-facter/blob/f34bcc754325d71bb3b1b534804e53d6170f15f5/index.js#23L10
- https://security.snyk.io/vuln/SNYK-JS-PUPPETFACTER-3175616
