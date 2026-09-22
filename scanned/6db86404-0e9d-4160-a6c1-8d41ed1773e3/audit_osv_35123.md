# [H] RDMA/rxe: Fix null deref on srq->rq.queue after resize failure

## Summary
Severity: High
Advisory: CVE-2025-68379
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68379
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix null deref on srq->rq.queue after resize failure

A NULL pointer dereference can occur in rxe_srq_chk_attr() when
ibv_modify_srq() is invoked twice in succession under certain error
conditions. The first call may fail in rxe_queue_resize(), which leads
rxe_srq_from_attr() to set srq->rq.queue = NULL. The second call then
triggers a crash (null deref) when accessing
srq->rq.queue->buf->index_mask.

Call Trace:
<TASK>
rxe_modify_srq+0x170/0x480 [rdma_rxe]
? __pfx_rxe_modify_srq+0x10/0x10 [rdma_rxe]
? uverbs_try_lock_object+0x4f/0xa0 [ib_uverbs]
? rdma_lookup_get_uobject+0x1f0/0x380 [ib_uverbs]
ib_uverbs_modify_srq+0x204/0x290 [ib_uverbs]
? __pfx_ib_uverbs_modify_srq+0x10/0x10 [ib_uverbs]
? tryinc_node_nr_active+0xe6/0x150
? uverbs_fill_udata+0xed/0x4f0 [ib_uverbs]
ib_uverbs_handler_UVERBS_METHOD_INVOKE_WRITE+0x2c0/0x470 [ib_uverbs]
? __pfx_ib_uverbs_handler_UVERBS_METHOD_INVOKE_WRITE+0x10/0x10 [ib_uverbs]
? uverbs_fill_udata+0xed/0x4f0 [ib_uverbs]
ib_uverbs_run_method+0x55a/0x6e0 [ib_uverbs]
? __pfx_ib_uverbs_handler_UVERBS_METHOD_INVOKE_WRITE+0x10/0x10 [ib_uverbs]
ib_uverbs_cmd_verbs+0x54d/0x800 [ib_uverbs]
? __pfx_ib_uverbs_cmd_verbs+0x10/0x10 [ib_uverbs]
? __pfx___raw_spin_lock_irqsave+0x10/0x10
? __pfx_do_vfs_ioctl+0x10/0x10
? ioctl_has_perm.constprop.0.isra.0+0x2c7/0x4c0
? __pfx_ioctl_has_perm.constprop.0.isra.0+0x10/0x10
ib_uverbs_ioctl+0x13e/0x220 [ib_uverbs]
? __pfx_ib_uverbs_ioctl+0x10/0x10 [ib_uverbs]
__x64_sys_ioctl+0x138/0x1c0
do_syscall_64+0x82/0x250
? fdget_pos+0x58/0x4c0
? ksys_write+0xf3/0x1c0
? __pfx_ksys_write+0x10/0x10
? do_syscall_64+0xc8/0x250
? __pfx_vm_mmap_pgoff+0x10/0x10
? fget+0x173/0x230
? fput+0x2a/0x80
? ksys_mmap_pgoff+0x224/0x4c0
? do_syscall_64+0xc8/0x250
? do_user_addr_fault+0x37b/0xfe0
? clear_bhb_loop+0x50/0xa0
? clear_bhb_loop+0x50/0xa0
? clear_bhb_loop+0x50/0xa0
entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/503a5e4690ae14c18570141bc0dcf7501a8419b0
- https://git.kernel.org/stable/c/58aca869babd48cb9c3d6ee9e1452c4b9f5266a6
- https://git.kernel.org/stable/c/5dbeb421e137824aa9bd8358bdfc926a3965fc0d
- https://git.kernel.org/stable/c/b8f6eeb87a76b6fb1f6381b0b2894568e1b784f7
- https://git.kernel.org/stable/c/bc4c14a3863cc0e03698caec9a0cdabd779776ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68379.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
