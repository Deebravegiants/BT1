# [H] CVE-2024-57259

## Summary
Severity: High
Advisory: CVE-2024-57259
CVSS: 7.1 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2024-57259
Type: osv

## Details
sqfs_search_dir in Das U-Boot before 2025.01-rc1 exhibits an off-by-one error and resultant heap memory corruption for squashfs directory listing because the path separator is not considered in a size calculation.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00001.html
- https://source.denx.de/u-boot/u-boot/-/commit/048d795bb5b3d9c5701b4855f5e74bcf6849bf5e
- https://www.openwall.com/lists/oss-security/2025/02/17/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57259.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57259
