# [M] f2fs: remove WARN_ON in f2fs_is_valid_blkaddr

## Summary
Severity: Medium
Advisory: CVE-2022-49318
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49318
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: remove WARN_ON in f2fs_is_valid_blkaddr

Syzbot triggers two WARNs in f2fs_is_valid_blkaddr and
__is_bitmap_valid. For example, in f2fs_is_valid_blkaddr,
if type is DATA_GENERIC_ENHANCE or DATA_GENERIC_ENHANCE_READ,
it invokes WARN_ON if blkaddr is not in the right range.
The call trace is as follows:

 f2fs_get_node_info+0x45f/0x1070
 read_node_page+0x577/0x1190
 __get_node_page.part.0+0x9e/0x10e0
 __get_node_page
 f2fs_get_node_page+0x109/0x180
 do_read_inode
 f2fs_iget+0x2a5/0x58b0
 f2fs_fill_super+0x3b39/0x7ca0

Fix these two WARNs by replacing WARN_ON with dump_stack.

## References
- https://git.kernel.org/stable/c/0a7a1fc7e71eecf2e5053a6c312c9f0dcbb9b8fd
- https://git.kernel.org/stable/c/32bea51fe4c6e92c00403739f7547c89219bea88
- https://git.kernel.org/stable/c/8c62c5e26345c34d199b4b8c8e69255ba3d0e751
- https://git.kernel.org/stable/c/99c09b298e47ebbe345a6da9f268b32a6b0f4582
- https://git.kernel.org/stable/c/cd6374af36cc548464d8c47a93fdba7303bb82a4
- https://git.kernel.org/stable/c/dc2f78e2d4cc844a1458653d57ce1b54d4a29f21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49318.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
