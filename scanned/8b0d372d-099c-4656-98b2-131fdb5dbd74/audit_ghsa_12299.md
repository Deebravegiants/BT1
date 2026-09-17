# [H] Regular Expression Denial of Service in semver

## Summary
Severity: High
Advisory: GHSA-x6fg-f45m-jf5q
CVE: CVE-2015-8855
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-x6fg-f45m-jf5q
Type: github-advisory

## Affected
- npm: `semver` — affected >=1.0.4 <4.3.2

## Details
Versions 4.3.1 and earlier of `semver` are affected by a regular expression denial of service vulnerability when extremely long version strings are parsed.



## Recommendation

Update to version 4.3.2 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8855
- https://github.com/github/advisory-database/pull/7102
- https://github.com/npm/node-semver/commit/5c4c9f6e26c7052a42b5ced2a7481c5c9b4363a0
- https://github.com/npm/node-semver/commit/c80180d8341a8ada0236815c29a2be59864afd70
- https://github.com/advisories/GHSA-x6fg-f45m-jf5q
- https://github.com/npm/node-semver
- https://www.npmjs.com/advisories/31
- https://www.owasp.org/index.php/Regular_expression_Denial_of_Service_-_ReDoS
- http://www.openwall.com/lists/oss-security/2016/04/20/11
- http://www.securityfocus.com/bid/86957
