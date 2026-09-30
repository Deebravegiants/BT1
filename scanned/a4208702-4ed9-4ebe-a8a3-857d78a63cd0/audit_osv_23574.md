# [M] watch_queue: Free the page array when watch_queue is dismantled

## Summary
Severity: Medium
Advisory: CVE-2022-49148
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49148
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

watch_queue: Free the page array when watch_queue is dismantled

Commit 7ea1a0124b6d ("watch_queue: Free the alloc bitmap when the
watch_queue is torn down") took care of the bitmap, but not the page
array.

  BUG: memory leak
  unreferenced object 0xffff88810d9bc140 (size 32):
  comm "syz-executor335", pid 3603, jiffies 4294946994 (age 12.840s)
  hex dump (first 32 bytes):
    40 a7 40 04 00 ea ff ff 00 00 00 00 00 00 00 00  @.@.............
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
     kmalloc_array include/linux/slab.h:621 [inline]
     kcalloc include/linux/slab.h:652 [inline]
     watch_queue_set_size+0x12f/0x2e0 kernel/watch_queue.c:251
     pipe_ioctl+0x82/0x140 fs/pipe.c:632
     vfs_ioctl fs/ioctl.c:51 [inline]
     __do_sys_ioctl fs/ioctl.c:874 [inline]
     __se_sys_ioctl fs/ioctl.c:860 [inline]
     __x64_sys_ioctl+0xfc/0x140 fs/ioctl.c:860
     do_syscall_x64 arch/x86/entry/common.c:50 [inline]

## References
- https://git.kernel.org/stable/c/375cd2536494cfbcdda84ae8b3e35bf19d0250b9
- https://git.kernel.org/stable/c/3963a5d1ff75585bddf0c3a918566a6be09d7520
- https://git.kernel.org/stable/c/4913daecd04addb41bc96a9175a885e1c19862a8
- https://git.kernel.org/stable/c/7169f60110915c8b53bffd43741fa020a75eb87a
- https://git.kernel.org/stable/c/b490207017ba237d97b735b2aa66dc241ccd18f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49148.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
