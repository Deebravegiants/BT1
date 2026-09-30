# [H] Directory Traversal in hostr

## Summary
Severity: High
Advisory: GHSA-xqqr-p362-6rmc
CVE: CVE-2017-16029
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-xqqr-p362-6rmc
Type: github-advisory

## Affected
- npm: `hostr` — affected >=0 <2.3.6

## Details
Affected versions of `hostr` are vulnerable to directory traversal which allows attackers to read files outside the current directory by sending `../` in the url path for GET requests.


## Recommendation

Upgrade to version 2.3.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16029
- https://github.com/henrytseng/hostr/issues/8
- https://github.com/henrytseng/hostr/issues/8)
- https://github.com/advisories/GHSA-xqqr-p362-6rmc
- https://www.npmjs.com/advisories/303
