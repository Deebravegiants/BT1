# [M] Prototype Pollution in node-jsonpointer

## Summary
Severity: Medium
Advisory: GHSA-282f-qqgm-c34q
CVE: CVE-2021-23807
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-282f-qqgm-c34q
Type: github-advisory

## Affected
- npm: `jsonpointer` — affected >=0 <5.0.0
- npm: `org.webjars.npm:json-pointer` — affected >=0 <5.0.0

## Details
This affects the package `jsonpointer` before `5.0.0`. A type confusion vulnerability can lead to a bypass of a previous Prototype Pollution fix when the pointer components are arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23807
- https://github.com/janl/node-jsonpointer/pull/51
- https://github.com/janl/node-jsonpointer/commit/a0345f3550cd9c4d89f33b126390202b89510ad4
- https://github.com/janl/node-jsonpointer
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1910273
- https://snyk.io/vuln/SNYK-JS-JSONPOINTER-1577288
