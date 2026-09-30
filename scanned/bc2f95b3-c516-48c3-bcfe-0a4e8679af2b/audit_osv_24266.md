# [H] f2fs: fix to do sanity check on summary info

## Summary
Severity: High
Advisory: CVE-2022-50753
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50753
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to do sanity check on summary info

As Wenqing Liu reported in bugzilla:

https://bugzilla.kernel.org/show_bug.cgi?id=216456

BUG: KASAN: use-after-free in recover_data+0x63ae/0x6ae0 [f2fs]
Read of size 4 at addr ffff8881464dcd80 by task mount/1013

CPU: 3 PID: 1013 Comm: mount Tainted: G        W          6.0.0-rc4 #1
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.15.0-1 04/01/2014
Call Trace:
 dump_stack_lvl+0x45/0x5e
 print_report.cold+0xf3/0x68d
 kasan_report+0xa8/0x130
 recover_data+0x63ae/0x6ae0 [f2fs]
 f2fs_recover_fsync_data+0x120d/0x1fc0 [f2fs]
 f2fs_fill_super+0x4665/0x61e0 [f2fs]
 mount_bdev+0x2cf/0x3b0
 legacy_get_tree+0xed/0x1d0
 vfs_get_tree+0x81/0x2b0
 path_mount+0x47e/0x19d0
 do_mount+0xce/0xf0
 __x64_sys_mount+0x12c/0x1a0
 do_syscall_64+0x38/0x90
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

The root cause is: in fuzzed image, SSA table is corrupted: ofs_in_node
is larger than ADDRS_PER_PAGE(), result in out-of-range access on 4k-size
page.

- recover_data
 - do_recover_data
  - check_index_in_prev_nodes
   - f2fs_data_blkaddr

This patch adds sanity check on summary info in recovery and GC flow
in where the flows rely on them.

After patch:
[   29.310883] F2FS-fs (loop0): Inconsistent ofs_in_node:65286 in summary, ino:0, nid:6, max:1018

## References
- https://git.kernel.org/stable/c/0922ad64ccefa3e483e84355942b86e13c8fea68
- https://git.kernel.org/stable/c/4a8e8bf280703e04e0b9d91f101e1fdd9a5bd09e
- https://git.kernel.org/stable/c/73687c53919f49dff3852155621dab7a35c52854
- https://git.kernel.org/stable/c/c6ad7fd16657ebd34a87a97d9588195aae87597d
- https://git.kernel.org/stable/c/c99860f9a75079f339ed7670425b1ac58f26e2ff
- https://git.kernel.org/stable/c/e168f819bfa42459b14f479e55ebd550bcc78899
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50753.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
