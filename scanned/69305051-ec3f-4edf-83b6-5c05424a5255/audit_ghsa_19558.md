# [M] bep/imagemeta allows a potentially large memory allocation in PNG and WebP parsing

## Summary
Severity: Medium
Advisory: GHSA-fmhh-rw3h-785m
CVE: CVE-2025-32025
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-fmhh-rw3h-785m
Type: github-advisory

## Affected
- Go: `github.com/bep/imagemeta` — affected >=0 <0.11.0

## Details
### Impact

The buffer created for parsing metadata for PNG and WebP images was only bounded by their input data type, which could lead to potentially large memory allocation, and unreasonably high for image metadata. Before `v0.11.0`, If you didn't trust the input images, this could be abused to construct denial-of-service attacks.

### Patches

`v0.11.0` added a 10 MB upper limit.

## References
- https://github.com/bep/imagemeta/security/advisories/GHSA-fmhh-rw3h-785m
- https://nvd.nist.gov/vuln/detail/CVE-2025-32025
- https://github.com/bep/imagemeta/commit/ee0de9b029f4e82106729f69559f27c9a404229d
- https://github.com/bep/imagemeta
