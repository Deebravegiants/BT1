# [C] node-bluetooth-serial-port is vulnerable to Buffer Overflow via the findSerialPortChannel 

## Summary
Severity: Critical
Advisory: GHSA-9jh3-4pc9-hq29
CVE: CVE-2023-26109
CWE: CWE-120
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-09
Source: https://github.com/advisories/GHSA-9jh3-4pc9-hq29
Type: github-advisory

## Affected
- npm: `node-bluetooth-serial-port` — affected >=0

## Details
All versions of the package node-bluetooth-serial-port are vulnerable to Buffer Overflow via the findSerialPortChannel method due to improper user input length validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26109
- https://github.com/tinyprinter/node-bluetooth-serial-port
- https://security.snyk.io/vuln/SNYK-JS-NODEBLUETOOTHSERIALPORT-3311820
