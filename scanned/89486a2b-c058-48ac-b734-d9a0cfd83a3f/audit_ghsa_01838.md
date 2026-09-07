# [M] Improperly Controlled Modification of Dynamically-Determined Object Attributes in express-mock-middleware

## Summary
Severity: Medium
Advisory: GHSA-v39h-qm32-8gwq
CVE: CVE-2020-7616
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-v39h-qm32-8gwq
Type: github-advisory

## Affected
- npm: `express-mock-middleware` — affected >=0

## Details
express-mock-middleware through 0.0.6 is vulnerable to Prototype Pollution. Exported functions by the package can be tricked into adding or modifying properties of the `Object.prototype`. Exploitation of this vulnerability requires creation of a new directory where an attack code can be placed which will then be exported by `express-mock-middleware`. As such, this is considered to be a low risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7616
- https://github.com/LingyuCoder/express-mock-middleware/blob/master/lib/index.js#L39
- https://snyk.io/vuln/SNYK-JS-EXPRESSMOCKMIDDLEWARE-564120
