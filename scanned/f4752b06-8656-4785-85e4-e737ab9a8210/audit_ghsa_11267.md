# [M] Go Images vulnerable to an out-of-memory error via a crafted TIFF file

## Summary
Severity: Medium
Advisory: GHSA-44p7-9xx4-hf2g
CVE: CVE-2026-33809
CWE: CWE-434, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-44p7-9xx4-hf2g
Type: github-advisory

## Affected
- Go: `golang.org/x/image` — affected >=0 <0.38.0

## Details
A maliciously crafted TIFF file can cause image decoding to attempt to allocate up 4GiB of memory, causing either excessive resource consumption or an out-of-memory error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33809
- https://cs.opensource.google/go/x/image
- https://go.dev/cl/757660
- https://go.dev/issue/78267
- https://pkg.go.dev/vuln/GO-2026-4815
