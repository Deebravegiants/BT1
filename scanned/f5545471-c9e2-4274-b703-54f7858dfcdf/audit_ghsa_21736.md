# [H] Prototype Pollution in @strikeentco/set

## Summary
Severity: High
Advisory: GHSA-39qv-prmh-x37f
CVE: CVE-2021-23497
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-05
Source: https://github.com/advisories/GHSA-39qv-prmh-x37f
Type: github-advisory

## Affected
- npm: `@strikeentco/set` — affected >=0 <1.0.2

## Details
This affects the package @strikeentco/set before 1.0.2. It allows an attacker to cause a denial of service and may lead to remote code execution. **Note:** This vulnerability derives from an incomplete fix in https://security.snyk.io/vuln/SNYK-JS-STRIKEENTCOSET-1038821

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23497
- https://github.com/strikeentco/set/commit/b2f942c
- https://github.com/strikeentco/set
- https://security.snyk.io/vuln/SNYK-JS-STRIKEENTCOSET-1038821
- https://snyk.io/blog/remediate-javascript-type-confusion-bypassed-input-validation
- https://snyk.io/vuln/SNYK-JS-STRIKEENTCOSET-2385945
