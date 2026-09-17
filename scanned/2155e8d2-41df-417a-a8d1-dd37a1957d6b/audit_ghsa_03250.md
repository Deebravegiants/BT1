# [C] OS Command Injection in wifiscanner

## Summary
Severity: Critical
Advisory: GHSA-m6rw-m2v9-7hx4
CVE: CVE-2020-15362
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-m6rw-m2v9-7hx4
Type: github-advisory

## Affected
- npm: `wifiscanner` — affected >=0

## Details
wifiscanner.js in thingsSDK WiFi Scanner 1.0.1 allows Code Injection because it can be used with options to overwrite the default executable/binary path and its arguments. An attacker can abuse this functionality to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15362
- https://github.com/thingsSDK/wifiscanner/issues/1
