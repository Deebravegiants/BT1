# [M] GoBGP has an Improper Resource Shutdown or Release

## Summary
Severity: Medium
Advisory: GHSA-vm3g-8xwv-mxfp
CVE: CVE-2026-7734
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-vm3g-8xwv-mxfp
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=0 <4.4.0

## Details
A vulnerability has been found in osrg GoBGP up to 4.3.0. This impacts the function SRv6L3ServiceAttribute.DecodeFromBytes of the file pkg/packet/bgp/prefix_sid.go of the component SRv6 L3 Service. Such manipulation of the argument data leads to denial of service. The attack may be performed from remote. Upgrading to version 4.4.0 will fix this issue. The name of the patch is f9f7b55ec258e514be0264871fa645a2c3edad11. Users should upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7734
- https://github.com/osrg/gobgp/commit/f9f7b55ec258e514be0264871fa645a2c3edad11
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/releases/tag/v4.4.0
- https://vuldb.com/submit/807581
- https://vuldb.com/vuln/360909
- https://vuldb.com/vuln/360909/cti
