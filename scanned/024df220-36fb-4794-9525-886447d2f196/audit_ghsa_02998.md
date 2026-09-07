# [M] Prototype Pollution in json-ptr

## Summary
Severity: Medium
Advisory: GHSA-8gwj-8hxc-285w
CVE: CVE-2021-23509
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-8gwj-8hxc-285w
Type: github-advisory

## Affected
- npm: `json-ptr` — affected >=0 <3.0.0

## Details
This affects the package `json-ptr` before `3.0.0`. A type confusion vulnerability can lead to a bypass of CVE-2020-7766 when the user-provided keys used in the pointer parameter are arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23509
- https://github.com/flitbit/json-ptr/pull/42
- https://github.com/flitbit/json-ptr/commit/5dc458fbad1c382a2e3ca6d62e66ede3d92849ca
- https://github.com/flitbit/json-ptr
- https://github.com/flitbit/json-ptr%23security-vulnerabilities-resolved
- https://snyk.io/vuln/SNYK-JS-JSONPTR-1577291
