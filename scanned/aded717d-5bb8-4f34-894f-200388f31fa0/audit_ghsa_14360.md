# [C] safe-eval vulnerable to Prototype Pollution via the safeEval function

## Summary
Severity: Critical
Advisory: GHSA-hcg3-56jf-x4vh
CVE: CVE-2023-26121
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-hcg3-56jf-x4vh
Type: github-advisory

## Affected
- npm: `safe-eval` — affected >=0

## Details
All versions of the package safe-eval are vulnerable to Prototype Pollution via the safeEval function, due to improper sanitization of its parameter content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26121
- https://github.com/hacksparrow/safe-eval/issues/28
- https://gist.github.com/seongil-wi/9d9fc0cc5b7b130419cd45827e59c4f9
- https://github.com/hacksparrow/safe-eval
- https://security.snyk.io/vuln/SNYK-JS-SAFEEVAL-3373062
