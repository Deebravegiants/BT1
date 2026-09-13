# [C] Code Injection in node-rules

## Summary
Severity: Critical
Advisory: GHSA-f78f-353m-cf4j
CVE: CVE-2020-7609
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-f78f-353m-cf4j
Type: github-advisory

## Affected
- npm: `node-rules` — affected >=3.0.0 <5.0.0

## Details
node-rules including 3.0.0 and prior to 5.0.0 allows injection of arbitrary commands. The argument rules of function "fromJSON()" can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7609
- https://github.com/mithunsatheesh/node-rules/issues/84
- https://github.com/mithunsatheesh/node-rules/commit/100862223904bb6478fcc33b701c7dee11f7b832
- https://snyk.io/vuln/SNYK-JS-NODERULES-560426
