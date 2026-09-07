# [H] GoBGP panics due to a zero value for softwareVersionLen

## Summary
Severity: High
Advisory: GHSA-7m35-vw2c-696v
CVE: CVE-2025-43971
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-7m35-vw2c-696v
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v3` — affected >=3.11.0 <3.35.0

## Details
An issue was discovered in GoBGP before 3.35.0 (introduced in v3.11.0). pkg/packet/bgp/bgp.go allows attackers to cause a panic via a zero value for softwareVersionLen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43971
- https://github.com/osrg/gobgp/commit/08a001e06d90e8bcc190084c66992f46f62c0986
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/compare/v3.34.0...v3.35.0
- https://security-tracker.debian.org/tracker/CVE-2025-43971
