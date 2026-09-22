# [M] GoBGP crashes in the flowspec parser

## Summary
Severity: Medium
Advisory: GHSA-mfvv-mgf6-q25r
CVE: CVE-2025-43972
CWE: CWE-1284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-mfvv-mgf6-q25r
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp` — affected >=0
- Go: `github.com/osrg/gobgp/v3` — affected >=0 <3.35.0

## Details
An issue was discovered in GoBGP before 3.35.0. An attacker can cause a crash in the pkg/packet/bgp/bgp.go flowspec parser by sending fewer than 20 bytes in a certain context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43972
- https://github.com/osrg/gobgp/commit/ca7383f450f7b296c5389feceef2467de5ab6e5a
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/compare/v3.34.0...v3.35.0
