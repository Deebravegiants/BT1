# [H] Prototype Pollution in bmoor

## Summary
Severity: High
Advisory: GHSA-4m8h-h59m-m34j
CVE: CVE-2021-23558
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-4m8h-h59m-m34j
Type: github-advisory

## Affected
- npm: `bmoor` — affected >=0 <0.10.1

## Details
The package bmoor before 0.10.1 is vulnerable to Prototype Pollution due to missing sanitization in set function. **Note:** This vulnerability derives from an incomplete fix in [CVE-2020-7736](https://security.snyk.io/vuln/SNYK-JS-BMOOR-598664)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23558
- https://github.com/b-heilman/bmoor/commit/29b0162cc1dc1791fc060891f568b0ae29bc542b
- https://github.com/b-heilman/bmoor
- https://security.snyk.io/vuln/SNYK-JS-BMOOR-598664
- https://snyk.io/blog/remediate-javascript-type-confusion-bypassed-input-validation
- https://snyk.io/vuln/SNYK-JS-BMOOR-2342622
