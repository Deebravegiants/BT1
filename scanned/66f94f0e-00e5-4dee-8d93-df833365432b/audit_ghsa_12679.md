# [H] progressbar.js vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-89qm-hm2x-mxm3
CVE: CVE-2023-26133
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-89qm-hm2x-mxm3
Type: github-advisory

## Affected
- npm: `progressbar.js` — affected >=0 <1.1.1

## Details
All versions of the package progressbar.js prior to 1.1.1 are vulnerable to Prototype Pollution via the function extend() in the file utils.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26133
- https://github.com/kimmobrunfeldt/progressbar.js/commit/97fe68ef4beccfe84b7cba08ea1fc695e38cc04b
- https://github.com/kimmobrunfeldt/progressbar.js
- https://github.com/kimmobrunfeldt/progressbar.js/blob/74536b9eeeaaf51144706d918ed5a0a679631d96/src/utils.js#L18
- https://github.com/kimmobrunfeldt/progressbar.js/blob/74536b9eeeaaf51144706d918ed5a0a679631d96/src/utils.js#L20
- https://security.snyk.io/vuln/SNYK-JS-PROGRESSBARJS-3184152
