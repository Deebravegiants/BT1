# [M] Marked ReDoS due to email addresses being evaluated in quadratic time

## Summary
Severity: Medium
Advisory: GHSA-xf5p-87ch-gxw2
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-xf5p-87ch-gxw2
Type: github-advisory

## Affected
- npm: `marked` — affected >=0.3.14 <0.6.2

## Details
Versions of `marked` from 0.3.14 until 0.6.2 are vulnerable to Regular Expression Denial of Service. Email addresses may be evaluated in quadratic time, allowing attackers to potentially crash the node process due to resource exhaustion.


## Recommendation

Upgrade to version 0.6.2 or later.

## References
- https://github.com/markedjs/marked/pull/1460
- https://github.com/markedjs/marked/commit/b15e42b67cec9ded8505e9d68bb8741ad7a9590d
- https://github.com/markedjs/marked
- https://github.com/markedjs/marked/releases/tag/v0.6.2
- https://snyk.io/vuln/SNYK-JS-MARKED-174116
- https://www.npmjs.com/advisories/812
