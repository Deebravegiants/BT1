# [H] free5gc Buffer Overflow vulnerability

## Summary
Severity: High
Advisory: GHSA-6944-6pmv-6mp2
CVE: CVE-2023-47345
CWE: CWE-120
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-6944-6pmv-6mp2
Type: github-advisory

## Affected
- Go: `github.com/free5gc/free5gc` — affected >=0

## Details
Buffer Overflow vulnerability in free5gc 3.3.0 allows attackers to cause a denial of service via crafted PFCP message with malformed PFCP Heartbeat message whose Recovery Time Stamp IE length is mutated to zero.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47345
- https://github.com/free5gc/free5gc/issues/483
- https://github.com/free5gc/free5gc
