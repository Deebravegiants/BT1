# [H] SQL injection in Apache Traffic Control

## Summary
Severity: High
Advisory: GHSA-vq94-9pfv-ccqr
CVE: CVE-2024-45387
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-vq94-9pfv-ccqr
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol/v8` — affected >=8.0.0 <8.0.2

## Details
An SQL injection vulnerability in Traffic Ops in Apache Traffic Control <= 8.0.1, >= 8.0.0 allows a privileged user with role "admin", "federation", "operations", "portal", or "steering" to execute arbitrary SQL against the database by sending a specially-crafted PUT request.

Users are recommended to upgrade to version Apache Traffic Control 8.0.2 if you run an affected version of Traffic Ops.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45387
- https://github.com/apache/trafficcontrol
- https://github.com/apache/trafficcontrol/releases/tag/v8.0.2
- https://lists.apache.org/thread/t38nk5n7t8w3pb66z7z4pqfzt4443trr
- http://www.openwall.com/lists/oss-security/2024/12/23/3
