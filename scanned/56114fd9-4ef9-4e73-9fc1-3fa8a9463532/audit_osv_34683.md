# [M] CVE-2025-63744

## Summary
Severity: Medium
Advisory: CVE-2025-63744
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-11-14
Source: https://osv.dev/vulnerability/CVE-2025-63744
Type: osv

## Details
A NULL pointer dereference vulnerability was discovered in radare2 6.0.5 and earlier within the load() function of bin_dyldcache.c. Processing a crafted file can cause a segmentation fault and crash the program.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63744.json
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-002-radare2-nullptr-deref-bin_dyldcache.md
- https://github.com/marlinkcyber/advisories/blob/main/advisories/radare2-nullptr-deref-bin_dyldcache.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-63744
- https://github.com/radareorg/radare2/issues/24661
- https://github.com/radareorg/radare2/commit/e37e15d10fd8a19c3e57b3d7735a2cfe0082ec79
