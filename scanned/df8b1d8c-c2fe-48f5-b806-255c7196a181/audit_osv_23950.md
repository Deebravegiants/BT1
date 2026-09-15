# [H] block: Fix handling of offline queues in blk_mq_alloc_request_hctx()

## Summary
Severity: High
Advisory: CVE-2022-49720
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49720
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: Fix handling of offline queues in blk_mq_alloc_request_hctx()

This patch prevents that test nvme/004 triggers the following:

UBSAN: array-index-out-of-bounds in block/blk-mq.h:135:9
index 512 is out of range for type 'long unsigned int [512]'
Call Trace:
 show_stack+0x52/0x58
 dump_stack_lvl+0x49/0x5e
 dump_stack+0x10/0x12
 ubsan_epilogue+0x9/0x3b
 __ubsan_handle_out_of_bounds.cold+0x44/0x49
 blk_mq_alloc_request_hctx+0x304/0x310
 __nvme_submit_sync_cmd+0x70/0x200 [nvme_core]
 nvmf_connect_io_queue+0x23e/0x2a0 [nvme_fabrics]
 nvme_loop_connect_io_queues+0x8d/0xb0 [nvme_loop]
 nvme_loop_create_ctrl+0x58e/0x7d0 [nvme_loop]
 nvmf_create_ctrl+0x1d7/0x4d0 [nvme_fabrics]
 nvmf_dev_write+0xae/0x111 [nvme_fabrics]
 vfs_write+0x144/0x560
 ksys_write+0xb7/0x140
 __x64_sys_write+0x42/0x50
 do_syscall_64+0x35/0x80
 entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/14dc7a18abbe4176f5626c13c333670da8e06aa1
- https://git.kernel.org/stable/c/7fa28a7c3d74933a4fc22d341b60927952f31c19
- https://git.kernel.org/stable/c/b202a0bd2580ee5b0453772c46d464152fafff73
- https://git.kernel.org/stable/c/b5e65ef044d627effdc2599040b6d204e003f955
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49720.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
