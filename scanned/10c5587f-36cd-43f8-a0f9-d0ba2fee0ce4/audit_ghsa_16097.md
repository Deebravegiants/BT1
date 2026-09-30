# [M] Safearchive Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q3rp-vvm7-j8jg
CVE: CVE-2024-10389
CWE: CWE-22, CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-q3rp-vvm7-j8jg
Type: github-advisory

## Affected
- Go: `github.com/google/safearchive` — affected >=0 <0.0.0-20241025131057-f7ce9d7b6f9c

## Details
There exists a Path Traversal vulnerability in Safearchive on Platforms with Case-Insensitive Filesystems (e.g., NTFS). This allows Attackers to Write Arbitrary Files via Archive Extraction containing symbolic links. We recommend upgrading past commit f7ce9d7b6f9c6ecd72d0b0f16216b046e55e44dc

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10389
- https://github.com/google/safearchive/commit/f7ce9d7b6f9c6ecd72d0b0f16216b046e55e44dc
- https://github.com/advisories/GHSA-q3rp-vvm7-j8jg
- https://github.com/google/safearchive
