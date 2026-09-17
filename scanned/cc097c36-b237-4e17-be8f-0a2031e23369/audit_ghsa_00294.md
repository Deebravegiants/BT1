# [H] Path Traversal in public

## Summary
Severity: High
Advisory: GHSA-rwv8-jvff-jq28
CVE: CVE-2018-3731
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-rwv8-jvff-jq28
Type: github-advisory

## Affected
- npm: `public` — affected >=0 <0.1.3

## Details
Versions of `public` before 0.1.3 are vulnerable to path traversal. This is due to lack of file path sanitization which could lead to any file the parent process has access to on the server to be read by malicious user.


## Recommendation

Update to version 0.1.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3731
- https://github.com/tnantoka/public/commit/eae8ad8017b260f8667ded5e12801bd72b877af2
- https://hackerone.com/reports/312918
- https://github.com/advisories/GHSA-rwv8-jvff-jq28
- https://www.npmjs.com/advisories/571
