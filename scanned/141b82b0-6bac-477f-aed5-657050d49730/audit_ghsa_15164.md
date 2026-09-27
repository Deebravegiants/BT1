# [M] stereoscope vulnerable to tar path traversal when processing OCI tar archives

## Summary
Severity: Medium
Advisory: GHSA-hpxr-w9w7-g4gv
CVE: CVE-2024-24579
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-hpxr-w9w7-g4gv
Type: github-advisory

## Affected
- Go: `github.com/anchore/stereoscope` — affected >=0 <0.0.1

## Details
### Impact
It is possible to craft an OCI tar archive that, when stereoscope attempts to unarchive the contents, will result in writing to paths outside of the unarchive temporary directory. Specifically, use of `github.com/anchore/stereoscope/pkg/file.UntarToDirectory()` function, the  `github.com/anchore/stereoscope/pkg/image/oci.TarballImageProvider` struct, or the higher level `github.com/anchore/stereoscope/pkg/image.Image.Read()` function express this vulnerability.

### Patches
Patched in v0.0.1

### Workarounds
If you are using the OCI archive as input into stereoscope then you can switch to using an [OCI layout](https://github.com/opencontainers/image-spec/blob/main/image-layout.md) by unarchiving the tar archive and provide the unarchived directory to stereoscope.

### References
- Patch PR https://github.com/anchore/stereoscope/pull/214

## References
- https://github.com/anchore/stereoscope/security/advisories/GHSA-hpxr-w9w7-g4gv
- https://nvd.nist.gov/vuln/detail/CVE-2024-24579
- https://github.com/anchore/stereoscope/commit/09dacab4d9ee65ee8bc7af8ebf4aa7b5aaa36204
- https://github.com/anchore/stereoscope
