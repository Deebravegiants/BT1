# [M] GoBGP does not verify that the input length

## Summary
Severity: Medium
Advisory: GHSA-c5jg-wr5v-2wp2
CVE: CVE-2025-43973
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-c5jg-wr5v-2wp2
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp` — affected >=0
- Go: `github.com/osrg/gobgp/v3` — affected >=0 <3.35.0

## Details
An issue was discovered in GoBGP before 3.35.0. pkg/packet/rtr/rtr.go does not verify that the input length corresponds to a situation in which all bytes are available for an RTR message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43973
- https://github.com/osrg/gobgp/commit/5693c58a4815cc6327b8d3b6980f0e5aced28abe
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/compare/v3.34.0...v3.35.0
