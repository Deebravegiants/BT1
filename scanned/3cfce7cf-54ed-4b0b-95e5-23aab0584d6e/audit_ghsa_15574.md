# [M] Grafana Alloy on Windows has Unquoted Search Path or Element vulnerability

## Summary
Severity: Medium
Advisory: GHSA-chqx-36rm-rf8h
CVE: CVE-2024-8975
CWE: CWE-428
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-chqx-36rm-rf8h
Type: github-advisory

## Affected
- Go: `github.com/grafana/alloy` — affected >=0 <1.3.4
- Go: `github.com/grafana/alloy` — affected >=1.4.0-rc.0 <1.4.1

## Details
Unquoted Search Path or Element vulnerability in Grafana Alloy on Windows allows Privilege Escalation from Local User to SYSTEM.
This issue affects Alloy: before 1.3.4, from 1.4.0-rc.0 and prior to 1.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8975
- https://github.com/grafana/alloy/commit/88e779887690954c009503598a3f4bf563cb6596
- https://github.com/grafana/alloy/commit/f14249012fd970d3fd73604e6fff9b6c7990a9bb
- https://github.com/grafana/alloy
- https://github.com/grafana/alloy/releases/tag/v1.3.4
- https://github.com/grafana/alloy/releases/tag/v1.4.0
- https://github.com/grafana/alloy/releases/tag/v1.4.1
- https://grafana.com/blog/2024/09/25/grafana-alloy-and-grafana-agent-flow-security-release-high-severity-fix-for-cve-2024-8975-and-cve-2024-8996
- https://grafana.com/security/security-advisories/cve-2024-8975
- https://pkg.go.dev/vuln/GO-2024-3168
