# [H] Directory Traversal in st

## Summary
Severity: High
Advisory: GHSA-69rr-wvh9-6c4q
CVE: CVE-2014-3744
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-69rr-wvh9-6c4q
Type: github-advisory

## Affected
- npm: `st` — affected >=0 <0.2.5

## Details
Versions of `st` prior to 0.2.5 are affected by a directory traversal vulnerability. Vulnerable versions fail to properly handle URL encoded dots, which caused `%2e` to be interpreted as `.` by the filesystem, resulting the potential for an attacker to read sensitive files on the server.


## Recommendation

Update to version 0.2.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3744
- https://github.com/isaacs/st
- https://github.com/isaacs/st#security-status
- https://www.npmjs.com/advisories/36
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
- http://www.securityfocus.com/bid/67389
