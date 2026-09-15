# [H] jfs: validate AG parameters in dbMount() to prevent crashes

## Summary
Severity: High
Advisory: CVE-2025-38230
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38230
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.143, >=6.2.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: validate AG parameters in dbMount() to prevent crashes

Validate db_agheight, db_agwidth, and db_agstart in dbMount to catch
corrupted metadata early and avoid undefined behavior in dbAllocAG.
Limits are derived from L2LPERCTL, LPERCTL/MAXAG, and CTLTREESIZE:

- agheight: 0 to L2LPERCTL/2 (0 to 5) ensures shift
  (L2LPERCTL - 2*agheight) >= 0.
- agwidth: 1 to min(LPERCTL/MAXAG, 2^(L2LPERCTL - 2*agheight))
  ensures agperlev >= 1.
  - Ranges: 1-8 (agheight 0-3), 1-4 (agheight 4), 1 (agheight 5).
  - LPERCTL/MAXAG = 1024/128 = 8 limits leaves per AG;
    2^(10 - 2*agheight) prevents division to 0.
- agstart: 0 to CTLTREESIZE-1 - agwidth*(MAXAG-1) keeps ti within
  stree (size 1365).
  - Ranges: 0-1237 (agwidth 1), 0-348 (agwidth 8).

UBSAN: shift-out-of-bounds in fs/jfs/jfs_dmap.c:1400:9
shift exponent -335544310 is negative
CPU: 0 UID: 0 PID: 5822 Comm: syz-executor130 Not tainted 6.14.0-rc5-syzkaller #0
Hardware name: Google Compute Engine/Google Compute Engine, BIOS Google 02/12/2025
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 ubsan_epilogue lib/ubsan.c:231 [inline]
 __ubsan_handle_shift_out_of_bounds+0x3c8/0x420 lib/ubsan.c:468
 dbAllocAG+0x1087/0x10b0 fs/jfs/jfs_dmap.c:1400
 dbDiscardAG+0x352/0xa20 fs/jfs/jfs_dmap.c:1613
 jfs_ioc_trim+0x45a/0x6b0 fs/jfs/jfs_discard.c:105
 jfs_ioctl+0x2cd/0x3e0 fs/jfs/ioctl.c:131
 vfs_ioctl fs/ioctl.c:51 [inline]
 __do_sys_ioctl fs/ioctl.c:906 [inline]
 __se_sys_ioctl+0xf5/0x170 fs/ioctl.c:892
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/0c40fa81f850556e9aa0185fede9ef1112db7b39
- https://git.kernel.org/stable/c/37bfb464ddca87f203071b5bd562cd91ddc0b40a
- https://git.kernel.org/stable/c/8b69608c6b6779a7ab07ce4467a56df90152cfb9
- https://git.kernel.org/stable/c/9242ff6245527a3ebb693ddd175493b38ddca72f
- https://git.kernel.org/stable/c/95ae5ee6069d9a5945772625f289422ef659221a
- https://git.kernel.org/stable/c/a4259e72363e1ea204a97292001a9fc36c7e52fd
- https://git.kernel.org/stable/c/b62a1e59d8716bbd2e73660743fe06acc97ed7d1
- https://git.kernel.org/stable/c/c3705c82b7406a15ef38a610d03bf6baa43d6e0c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38230.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
