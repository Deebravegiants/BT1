# [M] GoBGP does not properly check the input length

## Summary
Severity: Medium
Advisory: GHSA-hqhq-hp5x-xp3w
CVE: CVE-2025-43970
CWE: CWE-1284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-hqhq-hp5x-xp3w
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp` — affected >=0
- Go: `github.com/osrg/gobgp/v3` — affected >=0 <3.35.0

## Details
An issue was discovered in GoBGP before 3.35.0. pkg/packet/mrt/mrt.go does not properly check the input length, e.g., by ensuring that there are 12 bytes or 36 bytes (depending on the address family).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43970
- https://github.com/osrg/gobgp/commit/5153bafbe8dbe1a2f02a70bbf0365e98b80e47b0
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/compare/v3.34.0...v3.35.0
