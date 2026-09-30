# [H] nvme-rdma: unquiesce admin_q before destroy it

## Summary
Severity: High
Advisory: CVE-2024-49569
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-49569
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.6.88, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-rdma: unquiesce admin_q before destroy it

Kernel will hang on destroy admin_q while we create ctrl failed, such
as following calltrace:

PID: 23644    TASK: ff2d52b40f439fc0  CPU: 2    COMMAND: "nvme"
 #0 [ff61d23de260fb78] __schedule at ffffffff8323bc15
 #1 [ff61d23de260fc08] schedule at ffffffff8323c014
 #2 [ff61d23de260fc28] blk_mq_freeze_queue_wait at ffffffff82a3dba1
 #3 [ff61d23de260fc78] blk_freeze_queue at ffffffff82a4113a
 #4 [ff61d23de260fc90] blk_cleanup_queue at ffffffff82a33006
 #5 [ff61d23de260fcb0] nvme_rdma_destroy_admin_queue at ffffffffc12686ce
 #6 [ff61d23de260fcc8] nvme_rdma_setup_ctrl at ffffffffc1268ced
 #7 [ff61d23de260fd28] nvme_rdma_create_ctrl at ffffffffc126919b
 #8 [ff61d23de260fd68] nvmf_dev_write at ffffffffc024f362
 #9 [ff61d23de260fe38] vfs_write at ffffffff827d5f25
    RIP: 00007fda7891d574  RSP: 00007ffe2ef06958  RFLAGS: 00000202
    RAX: ffffffffffffffda  RBX: 000055e8122a4d90  RCX: 00007fda7891d574
    RDX: 000000000000012b  RSI: 000055e8122a4d90  RDI: 0000000000000004
    RBP: 00007ffe2ef079c0   R8: 000000000000012b   R9: 000055e8122a4d90
    R10: 0000000000000000  R11: 0000000000000202  R12: 0000000000000004
    R13: 000055e8122923c0  R14: 000000000000012b  R15: 00007fda78a54500
    ORIG_RAX: 0000000000000001  CS: 0033  SS: 002b

This due to we have quiesced admi_q before cancel requests, but forgot
to unquiesce before destroy it, as a result we fail to drain the
pending requests, and hang on blk_mq_freeze_queue_wait() forever. Here
try to reuse nvme_rdma_teardown_admin_queue() to fix this issue and
simplify the code.

## References
- https://git.kernel.org/stable/c/05b436f3cf65c957eff86c5ea5ddfa2604b32c63
- https://git.kernel.org/stable/c/427036030f4d796533dcadba9b845896cb6c10a7
- https://git.kernel.org/stable/c/5858b687559809f05393af745cbadf06dee61295
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49569.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
