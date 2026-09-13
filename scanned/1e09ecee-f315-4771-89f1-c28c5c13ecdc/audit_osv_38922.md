# [H] ocfs2: fix out-of-bounds write in ocfs2_write_end_inline

## Summary
Severity: High
Advisory: CVE-2026-43075
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43075
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix out-of-bounds write in ocfs2_write_end_inline

KASAN reports a use-after-free write of 4086 bytes in
ocfs2_write_end_inline, called from ocfs2_write_end_nolock during a
copy_file_range splice fallback on a corrupted ocfs2 filesystem mounted on
a loop device.  The actual bug is an out-of-bounds write past the inode
block buffer, not a true use-after-free.  The write overflows into an
adjacent freed page, which KASAN reports as UAF.

The root cause is that ocfs2_try_to_write_inline_data trusts the on-disk
id_count field to determine whether a write fits in inline data.  On a
corrupted filesystem, id_count can exceed the physical maximum inline data
capacity, causing writes to overflow the inode block buffer.

Call trace (crash path):

   vfs_copy_file_range (fs/read_write.c:1634)
     do_splice_direct
       splice_direct_to_actor
         iter_file_splice_write
           ocfs2_file_write_iter
             generic_perform_write
               ocfs2_write_end
                 ocfs2_write_end_nolock (fs/ocfs2/aops.c:1949)
                   ocfs2_write_end_inline (fs/ocfs2/aops.c:1915)
                     memcpy_from_folio     <-- KASAN: write OOB

So add id_count upper bound check in ocfs2_validate_inode_block() to
alongside the existing i_size check to fix it.

## References
- https://git.kernel.org/stable/c/0c1af902223b6fcedb60904ca0b551254686c7b9
- https://git.kernel.org/stable/c/22df7d4de9c5cd42edf855a1de25f2106088c4c6
- https://git.kernel.org/stable/c/2e6a254f9cedf51b75cc20b8b92e2209bfa04c3e
- https://git.kernel.org/stable/c/68f9cc3bbf2ae501770cea7dc0005fc9a85e48ea
- https://git.kernel.org/stable/c/69d3c69ade1e4285ab4ca48fe7acee0767e65604
- https://git.kernel.org/stable/c/7bc5da4842bed3252d26e742213741a4d0ac1b14
- https://git.kernel.org/stable/c/947f953978b0d9463498d548d0f054f5a75be2e9
- https://git.kernel.org/stable/c/e2c9dc6b6e96f3585f2a1062ca3374a52db0938f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
