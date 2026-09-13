# [H] Prototype Pollution in x-assign

## Summary
Severity: High
Advisory: GHSA-4mvj-rq4v-2fxw
CVE: CVE-2021-23452
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-10-21
Source: https://github.com/advisories/GHSA-4mvj-rq4v-2fxw
Type: github-advisory

## Affected
- npm: `x-assign` — affected >=0

## Details
This vulnerability affects all versions of package x-assign. The global proto object can be polluted using the __proto__ object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23452
- https://github.com/mvoorberg/x-assign
- https://runkit.com/embed/sq8qjwemyn8t
- https://snyk.io/vuln/SNYK-JS-XASSIGN-1759314
