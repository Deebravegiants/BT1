# [H] golang.org/x/image/tiff has excessive resource consumption in PackBits decompression

## Summary
Severity: High
Advisory: GHSA-q675-qj96-32m9
CVE: CVE-2026-46599
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-q675-qj96-32m9
Type: github-advisory

## Affected
- Go: `golang.org/x/image` — affected >=0 <0.41.0

## Details
The TIFF decoder does not place a limit on the size of PackBits-compressed data. A maliciously-crafted image can exploit this to cause a small image (both in terms of pixel width/height and encoded size) to make the decoder decode large amounts of compressed data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46599
- https://cs.opensource.google/go/x/image
- https://go.dev/cl/759960
- https://go.dev/issue/79577
- https://groups.google.com/g/golang-announce/c/uhYX90BlBvI
- https://pkg.go.dev/vuln/GO-2026-5032
