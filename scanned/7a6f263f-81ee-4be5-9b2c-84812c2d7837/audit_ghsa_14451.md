# [C] node-bluetooth is vulnerable to Buffer Overflow via the findSerialPortChannel method due to improper user input length validation

## Summary
Severity: Critical
Advisory: GHSA-cxx3-36qc-m6qm
CVE: CVE-2023-26110
CWE: CWE-120
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-09
Source: https://github.com/advisories/GHSA-cxx3-36qc-m6qm
Type: github-advisory

## Affected
- npm: `node-bluetooth` — affected >=0

## Details
All versions of the package node-bluetooth are vulnerable to Buffer Overflow via the findSerialPortChannel method due to improper user input length validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26110
- https://github.com/song940/node-bluetooth
- https://security.snyk.io/vuln/SNYK-JS-NODEBLUETOOTH-3311821
