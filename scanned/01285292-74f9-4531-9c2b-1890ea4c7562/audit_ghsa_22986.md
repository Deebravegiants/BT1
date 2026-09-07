# [M] cnlh nps vulnerable to file overwrite by local user

## Summary
Severity: Medium
Advisory: GHSA-2vp2-8m5j-4rjx
CVE: CVE-2019-15119
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2vp2-8m5j-4rjx
Type: github-advisory

## Affected
- Go: `ehang.io/nps` — affected >=0 <0.23.2

## Details
`lib/install/install.go` in cnlh nps prior to 0.23.2 uses 0777 permissions for `/usr/local/bin/nps and/or /usr/bin/nps`, leading to a file overwrite by a local user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15119
- https://github.com/cnlh/nps/issues/176
- https://github.com/cnlh/nps/commit/7178b3380720e910d283036a8d39879a94105515
- https://github.com/cnlh/nps
