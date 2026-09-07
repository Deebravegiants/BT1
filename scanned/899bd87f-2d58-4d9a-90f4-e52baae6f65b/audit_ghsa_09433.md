# [H] GoBGP has an out-of-bounds read in the ParseIP6Extended function

## Summary
Severity: High
Advisory: GHSA-wmvj-f67g-qg4g
CVE: CVE-2026-37461
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-wmvj-f67g-qg4g
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=0 <4.4.0

## Details
An out-of-bounds read in the ParseIP6Extended function (/bgp/bgp.go) of gobgp v4.3.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted BGP UPDATE message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37461
- https://github.com/osrg/gobgp/commit/362cce3e325f56e7a4f792ccb9689b3bdda9e682
- https://github.com/osrg/gobgp/commit/9ce8936672ebc07df524da77fa4c6ae26d92be6d
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/blob/v4.3.0/pkg/packet/bgp/bgp.go
