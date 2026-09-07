# [M] deep-parse-json vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-ff9j-pwxg-q5p2
CVE: CVE-2022-42743
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-04
Source: https://github.com/advisories/GHSA-ff9j-pwxg-q5p2
Type: github-advisory

## Affected
- npm: `deep-parse-json` — affected >=0

## Details
deep-parse-json version 1.0.2 allows an external attacker to edit or add new properties to an object. This is possible because the application does not correctly validate the incoming JSON keys, thus allowing the `__proto__` property to be edited.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42743
- https://github.com/sibu-github/deep-parse-json/issues/6
- https://fluidattacks.com/advisories/buuren
- https://github.com/sibu-github/deep-parse-json
