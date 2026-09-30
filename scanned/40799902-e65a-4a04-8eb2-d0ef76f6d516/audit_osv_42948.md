# [C] ntfs: validate index block header more strictly

## Summary
Severity: Critical
Advisory: CVE-2026-72206
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72206
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: validate index block header more strictly

Modify ntfs_index_block_inconsisent() to perform stricter validation of
INDEX_HEADER geometry in INDX blocks, and update
ntfs_lookup_inode_by_name() to use that function to validate INDX
blocks.

## References
- https://git.kernel.org/stable/c/14bc34fe948523dc2b0174691f9af9e74eb4f3fd
- https://git.kernel.org/stable/c/34a49b3e94a50f45b62c6e6f574f676a079ba23e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
