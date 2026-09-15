# [H] f2fs: fix to do sanity check on block address in f2fs_do_zero_range()

## Summary
Severity: High
Advisory: CVE-2022-49363
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49363
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to do sanity check on block address in f2fs_do_zero_range()

As Yanming reported in bugzilla:

https://bugzilla.kernel.org/show_bug.cgi?id=215894

I have encountered a bug in F2FS file system in kernel v5.17.

I have uploaded the system call sequence as case.c, and a fuzzed image can
be found in google net disk

The kernel should enable CONFIG_KASAN=y and CONFIG_KASAN_INLINE=y. You can
reproduce the bug by running the following commands:

kernel BUG at fs/f2fs/segment.c:2291!
Call Trace:
 f2fs_invalidate_blocks+0x193/0x2d0
 f2fs_fallocate+0x2593/0x4a70
 vfs_fallocate+0x2a5/0xac0
 ksys_fallocate+0x35/0x70
 __x64_sys_fallocate+0x8e/0xf0
 do_syscall_64+0x3b/0x90
 entry_SYSCALL_64_after_hwframe+0x44/0xae

The root cause is, after image was fuzzed, block mapping info in inode
will be inconsistent with SIT table, so in f2fs_fallocate(), it will cause
panic when updating SIT with invalid blkaddr.

Let's fix the issue by adding sanity check on block address before updating
SIT table with it.

## References
- https://git.kernel.org/stable/c/25f8236213a91efdf708b9d77e9e51b6fc3e141c
- https://git.kernel.org/stable/c/470493be19a5730ed432e3ac0f29a2ee7fc6c557
- https://git.kernel.org/stable/c/7361c9f2bd6a8f0cbb41cdea9aff04765ff23f67
- https://git.kernel.org/stable/c/805b48b234a2803cb7daec7f158af12f0fbaefac
- https://git.kernel.org/stable/c/a34d7b49894b0533222188a52e2958750f830efd
- https://git.kernel.org/stable/c/f2e1c38b5ac64eb1a16a89c52fb419409d12c25b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49363.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49363
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
