# [H] GoBGP: Integer underflow in the BGPUpdate.DecodeFromBytes function

## Summary
Severity: High
Advisory: GHSA-pw7p-7fqv-hpj8
CVE: CVE-2026-37462
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-pw7p-7fqv-hpj8
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=0 <4.4.0

## Details
An integer underflow in the BGPUpdate.DecodeFromBytes function (/bgp/bgp.go) of gobgp v4.3.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted BGP UPDATE message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37462
- https://github.com/osrg/gobgp/commit/9ce8936672ebc07df524da77fa4c6ae26d92be6d
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/blob/v4.3.0/pkg/packet/bgp/bgp.go
