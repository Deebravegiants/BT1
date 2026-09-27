# [M] RDMA/hns: Fix NULL pointer problem in free_mr_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49930
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49930
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix NULL pointer problem in free_mr_init()

Lock grab occurs in a concurrent scenario, resulting in stepping on a NULL
pointer.  It should be init mutex_init() first before use the lock.

  Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
  Call trace:
   __mutex_lock.constprop.0+0xd0/0x5c0
   __mutex_lock_slowpath+0x1c/0x2c
   mutex_lock+0x44/0x50
   free_mr_send_cmd_to_hw+0x7c/0x1c0 [hns_roce_hw_v2]
   hns_roce_v2_dereg_mr+0x30/0x40 [hns_roce_hw_v2]
   hns_roce_dereg_mr+0x4c/0x130 [hns_roce_hw_v2]
   ib_dereg_mr_user+0x54/0x124
   uverbs_free_mr+0x24/0x30
   destroy_hw_idr_uobject+0x38/0x74
   uverbs_destroy_uobject+0x48/0x1c4
   uobj_destroy+0x74/0xcc
   ib_uverbs_cmd_verbs+0x368/0xbb0
   ib_uverbs_ioctl+0xec/0x1a4
   __arm64_sys_ioctl+0xb4/0x100
   invoke_syscall+0x50/0x120
   el0_svc_common.constprop.0+0x58/0x190
   do_el0_svc+0x30/0x90
   el0_svc+0x2c/0xb4
   el0t_64_sync_handler+0x1a4/0x1b0
   el0t_64_sync+0x19c/0x1a0

## References
- https://git.kernel.org/stable/c/0e23e85d86b78e734dd6654f1b69fbaeb5534c81
- https://git.kernel.org/stable/c/12bcaf87d8b66d8cd812479c8a6349dcb245375c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49930.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
