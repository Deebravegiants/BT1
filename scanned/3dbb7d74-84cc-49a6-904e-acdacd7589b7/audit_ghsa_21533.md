# [M] fastest-json-copy vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-p5g9-rjcf-95vj
CVE: CVE-2022-41714
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-04
Source: https://github.com/advisories/GHSA-p5g9-rjcf-95vj
Type: github-advisory

## Affected
- npm: `fastest-json-copy` — affected >=0

## Details
fastest-json-copy version 1.0.1 allows an external attacker to edit or add new properties to an object. This is possible because the application does not correctly validate the incoming JSON keys, thus allowing the `__proto__` property to be edited.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41714
- https://fluidattacks.com/advisories/guetta
- https://github.com/streamich/fastest-json-copy
