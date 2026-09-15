# [M] Denial of Service in url-relative

## Summary
Severity: Medium
Advisory: GHSA-86p3-4gfq-38f2
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-86p3-4gfq-38f2
Type: github-advisory

## Affected
- npm: `url-relative` — affected >=0

## Details
All versions of `url-relative` are vulnerable to Denial of Service. If the values `to` and `from` are equal, the function hangs and never returns. This may cause a Denial of Service.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/junosuarez/url-relative/issues/3
- https://snyk.io/vuln/SNYK-JS-URLRELATIVE-173691
- https://www.npmjs.com/advisories/783
