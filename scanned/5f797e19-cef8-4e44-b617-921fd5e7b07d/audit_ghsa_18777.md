# [M] Slack Nebula may accept arbitrary source IP addresses 

## Summary
Severity: Medium
Advisory: GHSA-x6fh-7qmf-69xh
CVE: CVE-2025-62820
CWE: CWE-420
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-x6fh-7qmf-69xh
Type: github-advisory

## Affected
- Go: `github.com/slackhq/nebula` — affected >=1.9.4 <1.9.7

## Details
Slack Nebula before 1.9.7 mishandles CIDR in some configurations and thus accepts arbitrary source IP addresses within the Nebula network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62820
- https://github.com/slackhq/nebula/pull/1493
- https://github.com/slackhq/nebula/pull/1494
- https://github.com/slackhq/nebula/commit/e264a0ff888c7bf0568579306755a60fc42f6ecc
- https://github.com/slackhq/nebula
