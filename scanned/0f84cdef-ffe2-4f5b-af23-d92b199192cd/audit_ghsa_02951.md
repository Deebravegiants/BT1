# [M] Prototype Pollution in json-pointer

## Summary
Severity: Medium
Advisory: GHSA-v5vg-g7rq-363w
CVE: CVE-2021-23820
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-v5vg-g7rq-363w
Type: github-advisory

## Affected
- npm: `json-pointer` — affected >=0 <0.6.2

## Details
This affects versions of package `json-pointer` up to and including `0.6.1`. A type confusion vulnerability can lead to a bypass of CVE-2020-7709 when the pointer components are arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23820
- https://github.com/manuelstofer/json-pointer/pull/36
- https://github.com/manuelstofer/json-pointer/commit/931b0f9c7178ca09778087b4b0ac7e4f505620c2
- https://github.com/manuelstofer/json-pointer
- https://github.com/manuelstofer/json-pointer/blob/master/index.js%23L78
- https://snyk.io/vuln/SNYK-JS-JSONPOINTER-1577287
