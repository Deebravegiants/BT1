# [M] bep/imagemeta allows excessively large EXIF data structures

## Summary
Severity: Medium
Advisory: GHSA-q7rw-w4cq-2j6w
CVE: CVE-2025-32024
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-q7rw-w4cq-2j6w
Type: github-advisory

## Affected
- Go: `github.com/bep/imagemeta` — affected >=0 <0.10.0

## Details
### Impact
The EXIF data format allows for defining excessively large data structures in relatively small payloads. Before `v0.10.0`, If you didn't trust the input images, this could be abused to construct denial-of-service attacks.

### Patches
`v0.10.0` added LimitNumTags (default 5000) and LimitTagSize (default 10000) options.

## References
- https://github.com/bep/imagemeta/security/advisories/GHSA-q7rw-w4cq-2j6w
- https://nvd.nist.gov/vuln/detail/CVE-2025-32024
- https://github.com/bep/imagemeta/commit/4fd89616d8bf7f9bb892360d3fb19080ec2b4602
- https://github.com/bep/imagemeta
