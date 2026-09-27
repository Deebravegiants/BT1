# [M] Directory Traversal in serve

## Summary
Severity: Medium
Advisory: GHSA-q2qh-cgc2-qhr3
CVE: CVE-2018-3712
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-q2qh-cgc2-qhr3
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <6.4.9

## Details
Affected versions of `serve` do not properly handle `%2e` (.) and `%2f` (/) characters, and allow the, characters to be used in paths. This can be used to traverse the directory tree and list content of any directory the user running the process has access to.

Mitigating factors:
This vulnerability only allows listing of directory contents and does not allow reading of arbitrary files.


## Recommendation

Update to version 6.4.9 later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3712
- https://github.com/zeit/serve/pull/316
- https://github.com/vercel/serve/commit/6adad6881c61991da61ebc857857c53409544575
- https://hackerone.com/reports/307666
- https://github.com/vercel/serve
