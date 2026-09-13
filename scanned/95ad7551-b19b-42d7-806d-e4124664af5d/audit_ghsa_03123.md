# [C] Prototype pollution in json8

## Summary
Severity: Critical
Advisory: GHSA-7h43-gx24-p529
CVE: CVE-2020-7770
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-7h43-gx24-p529
Type: github-advisory

## Affected
- npm: `json8` — affected >=0 <1.0.3

## Details
This affects the package json8 before 1.0.3. The function adds in the target object the property specified in the path, however it does not properly check the key being set, leading to a prototype pollution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7770
- https://github.com/sonnyp/JSON8/commit/2e890261b66cbc54ae01d0c79c71b0fd18379e7e
- https://snyk.io/vuln/SNYK-JS-JSON8-1017116
- https://www.npmjs.com/package/json8
