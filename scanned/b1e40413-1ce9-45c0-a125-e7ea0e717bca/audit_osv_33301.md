# [H] fs: udf: fix OOB read in lengthAllocDescs handling

## Summary
Severity: High
Advisory: CVE-2025-40044
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40044
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: udf: fix OOB read in lengthAllocDescs handling

When parsing Allocation Extent Descriptor, lengthAllocDescs comes from
on-disk data and must be validated against the block size. Crafted or
corrupted images may set lengthAllocDescs so that the total descriptor
length (sizeof(allocExtDesc) + lengthAllocDescs) exceeds the buffer,
leading udf_update_tag() to call crc_itu_t() on out-of-bounds memory and
trigger a KASAN use-after-free read.

BUG: KASAN: use-after-free in crc_itu_t+0x1d5/0x2b0 lib/crc-itu-t.c:60
Read of size 1 at addr ffff888041e7d000 by task syz-executor317/5309

CPU: 0 UID: 0 PID: 5309 Comm: syz-executor317 Not tainted 6.12.0-rc4-syzkaller-00261-g850925a8133c #0
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2~bpo12+1 04/01/2014
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:377 [inline]
 print_report+0x169/0x550 mm/kasan/report.c:488
 kasan_report+0x143/0x180 mm/kasan/report.c:601
 crc_itu_t+0x1d5/0x2b0 lib/crc-itu-t.c:60
 udf_update_tag+0x70/0x6a0 fs/udf/misc.c:261
 udf_write_aext+0x4d8/0x7b0 fs/udf/inode.c:2179
 extent_trunc+0x2f7/0x4a0 fs/udf/truncate.c:46
 udf_truncate_tail_extent+0x527/0x7e0 fs/udf/truncate.c:106
 udf_release_file+0xc1/0x120 fs/udf/file.c:185
 __fput+0x23f/0x880 fs/file_table.c:431
 task_work_run+0x24f/0x310 kernel/task_work.c:239
 exit_task_work include/linux/task_work.h:43 [inline]
 do_exit+0xa2f/0x28e0 kernel/exit.c:939
 do_group_exit+0x207/0x2c0 kernel/exit.c:1088
 __do_sys_exit_group kernel/exit.c:1099 [inline]
 __se_sys_exit_group kernel/exit.c:1097 [inline]
 __x64_sys_exit_group+0x3f/0x40 kernel/exit.c:1097
 x64_sys_call+0x2634/0x2640 arch/x86/include/generated/asm/syscalls_64.h:232
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
 </TASK>

Validate the computed total length against epos->bh->b_size.

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/14496175b264d30c2045584ee31d062af2e3a660
- https://git.kernel.org/stable/c/1d1847812a1a5375c10a2a779338df643f79c047
- https://git.kernel.org/stable/c/3bd5e45c2ce30e239d596becd5db720f7eb83c99
- https://git.kernel.org/stable/c/459404f858213967ccfff336c41747d8dd186d38
- https://git.kernel.org/stable/c/918649364fbca7d5df72522ca795479edcd25f91
- https://git.kernel.org/stable/c/a70dcfa8d0a0cc530a6af59483dfca260b652c1b
- https://git.kernel.org/stable/c/b57f2d7d3e6bb89ed82330c5fe106cdfa34d3e24
- https://git.kernel.org/stable/c/d2ed9aa8ae50fb0d4ac5ab07e4c67ba7e9a24818
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40044.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40044
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
