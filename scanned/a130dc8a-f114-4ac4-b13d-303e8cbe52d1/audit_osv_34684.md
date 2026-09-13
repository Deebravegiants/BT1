# [M] CVE-2025-63745

## Summary
Severity: Medium
Advisory: CVE-2025-63745
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-14
Source: https://osv.dev/vulnerability/CVE-2025-63745
Type: osv

## Details
A NULL pointer dereference vulnerability was discovered in radare2 6.0.5 and earlier within the info() function of bin_ne.c. A crafted binary input can trigger a segmentation fault, leading to a denial of service when the tool processes malformed data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63745.json
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-001-radare2-nullptr-deref-bin_ne.md
- https://github.com/marlinkcyber/advisories/blob/main/advisories/radare2-nullptr-deref-bin_ne.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-63745
- https://github.com/radareorg/radare2/issues/24660
- https://github.com/radareorg/radare2/commit/6c5df3f8570d4f0c360681c08241ad8af3b919fd
