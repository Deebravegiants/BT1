# [H] Brokercap Bifrost subject to authentication bypass when using HTTP basic authentication

## Summary
Severity: High
Advisory: GHSA-p6fh-xc6r-g5hw
CVE: CVE-2022-39219
CWE: CWE-287, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-p6fh-xc6r-g5hw
Type: github-advisory

## Affected
- Go: `github.com/brokercap/Bifrost` — affected >=0 <1.8.7-release

## Details
Bifrost is a middleware package which can synchronize MySQL/MariaDB binlog data to other types of databases. Versions 1.8.6-release and prior are vulnerable to authentication bypass when using HTTP basic authentication. This may allow group members who only have read permissions to write requests when they are normally forbidden from doing so. Version 1.8.7-release contains a patch. There are currently no known workarounds.

## References
- https://github.com/brokercap/Bifrost/security/advisories/GHSA-p6fh-xc6r-g5hw
- https://nvd.nist.gov/vuln/detail/CVE-2022-39219
- https://github.com/brokercap/Bifrost/issues/200
- https://github.com/brokercap/Bifrost
- https://github.com/brokercap/Bifrost/releases/tag/v1.8.7-release
