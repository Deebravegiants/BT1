# [H] CVE-2024-57256

## Summary
Severity: High
Advisory: CVE-2024-57256
CVSS: 7.1 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2024-57256
Type: osv

## Details
An integer overflow in ext4fs_read_symlink in Das U-Boot before 2025.01-rc1 occurs for zalloc (adding one to an le32 variable) via a crafted ext4 filesystem with an inode size of 0xffffffff, resulting in a malloc of zero and resultant memory overwrite.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00001.html
- https://source.denx.de/u-boot/u-boot/-/commit/35f75d2a46e5859138c83a75cd2f4141c5479ab9
- https://www.openwall.com/lists/oss-security/2025/02/17/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57256.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57256
