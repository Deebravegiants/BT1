# [H] Prototype Pollution in cached-path-relative

## Summary
Severity: High
Advisory: GHSA-hc9w-4p87-j549
CVE: CVE-2018-16472
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-07
Source: https://github.com/advisories/GHSA-hc9w-4p87-j549
Type: github-advisory

## Affected
- npm: `cached-path-relative` — affected >=0 <1.0.2

## Details
Version of `cached-path-relative` before 1.0.2 are vulnerable to prototype pollution.


## Recommendation

Update to version 1.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16472
- https://github.com/ashaffer/cached-path-relative/issues/3
- https://hackerone.com/reports/390847
- https://github.com/advisories/GHSA-hc9w-4p87-j549
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/480.json
- https://lists.debian.org/debian-lts-announce/2022/12/msg00006.html
- https://www.npmjs.com/advisories/739
