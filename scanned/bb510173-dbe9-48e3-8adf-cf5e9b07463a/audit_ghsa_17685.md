# [M] OSV-SCALIBR's Container Image Unpacking Vulnerable to Arbitrary File Write via Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-2hcm-q3f4-fjgw
CVE: CVE-2025-5981
CWE: CWE-22, CWE-427
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2025-06-18
Source: https://github.com/advisories/GHSA-2hcm-q3f4-fjgw
Type: github-advisory

## Affected
- Go: `github.com/google/osv-scalibr` — affected >=0.1.3 <0.2.1

## Details
Arbitrary file write as the OSV-SCALIBR user on the host system via a path traversal vulnerability when using OSV-SCALIBR's unpack() function for container images. Particularly, when using the CLI flag --remote-image on untrusted container images.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5981
- https://github.com/google/osv-scalibr/commit/2444419b1818c2d6917fc3394c947fb3276e9d59
- https://github.com/google/osv-scalibr
- https://github.com/google/osv-scalibr/releases/tag/v0.1.8
- https://pkg.go.dev/vuln/GO-2025-3767
