# [M] flatten-json Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-j8px-pjmp-325f
CVE: CVE-2024-36574
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-j8px-pjmp-325f
Type: github-advisory

## Affected
- npm: `@allanlancioni/flatten-json` — affected >=0

## Details
A Prototype Pollution issue in flatten-json 1.0.1 allows an attacker to execute arbitrary code via module.exports.unflattenJSON (flatten-json/index.js:42)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36574
- https://gist.github.com/mestrtee/d5a0c93459599f77557b5bbe78b57325
- https://github.com/AllanLancioni/flatten-json
