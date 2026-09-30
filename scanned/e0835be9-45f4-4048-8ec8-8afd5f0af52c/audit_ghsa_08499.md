# [M] HashiCorp Nomad’s exec2 task driver vulnerable to a symlink attack

## Summary
Severity: Medium
Advisory: GHSA-wqwc-x3rc-2xw6
CVE: CVE-2026-8052
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-wqwc-x3rc-2xw6
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad-driver-exec2` — affected >=0 <0.1.2

## Details
HashiCorp Nomad’s exec2 task driver prior to 0.1.2 is vulnerable to arbitrary file read and write on the client host as the Nomad process user through a symlink attack. This vulnerability (CVE-2026-8052) is fixed in version 0.1.2 of the exec2 task driver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8052
- https://discuss.hashicorp.com/t/hcsec-2026-13-nomads-exec2-task-driver-vulnerable-to-arbitrary-file-read-write-on-client-host-through-symlink-attack/77415
- https://github.com/hashicorp/nomad-driver-exec2
- https://github.com/hashicorp/nomad-driver-exec2/releases/tag/v0.1.2
