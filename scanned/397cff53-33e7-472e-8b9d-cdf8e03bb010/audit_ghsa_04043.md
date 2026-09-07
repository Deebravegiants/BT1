# [M] Cross-Site Scripting in simditor

## Summary
Severity: Medium
Advisory: GHSA-8v67-x8q5-3x3g
CVE: CVE-2018-19048
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-8v67-x8q5-3x3g
Type: github-advisory

## Affected
- npm: `simditor` — affected >=0 <2.3.22

## Details
Versions of `simditor` prior to 2.3.22 are vulnerable to Cross-Site Scripting. The package does not sanitize user input that is rendered with `innerHTML`, allowing attackers to execute arbitrary JavaScript.


## Recommendation

Upgrade to version 2.3.22 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19048
- https://github.com/mycolorway/simditor/commit/ef01a643cbb7f8163535d6bfb71135f80ec6a6fd
- https://github.com/hkglue/simditor_demo.git
- https://github.com/hkglue/simditor_dom_xss/blob/master/README.md
- https://github.com/mycolorway/simditor/releases/tag/v2.3.22
- https://snyk.io/vuln/SNYK-JS-SIMDITOR-174638
- https://www.npmjs.com/advisories/884
