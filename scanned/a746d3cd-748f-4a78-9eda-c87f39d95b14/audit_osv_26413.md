# [H] drm/amdkfd: Fix an illegal memory access

## Summary
Severity: High
Advisory: CVE-2023-53090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53090
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.19.279, >=4.20.0 <5.4.238, >=5.5.0 <5.10.176, >=5.11.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix an illegal memory access

In the kfd_wait_on_events() function, the kfd_event_waiter structure is
allocated by alloc_event_waiters(), but the event field of the waiter
structure is not initialized; When copy_from_user() fails in the
kfd_wait_on_events() function, it will enter exception handling to
release the previously allocated memory of the waiter structure;
Due to the event field of the waiters structure being accessed
in the free_waiters() function, this results in illegal memory access
and system crash, here is the crash log:

localhost kernel: RIP: 0010:native_queued_spin_lock_slowpath+0x185/0x1e0
localhost kernel: RSP: 0018:ffffaa53c362bd60 EFLAGS: 00010082
localhost kernel: RAX: ff3d3d6bff4007cb RBX: 0000000000000282 RCX: 00000000002c0000
localhost kernel: RDX: ffff9e855eeacb80 RSI: 000000000000279c RDI: ffffe7088f6a21d0
localhost kernel: RBP: ffffe7088f6a21d0 R08: 00000000002c0000 R09: ffffaa53c362be64
localhost kernel: R10: ffffaa53c362bbd8 R11: 0000000000000001 R12: 0000000000000002
localhost kernel: R13: ffff9e7ead15d600 R14: 0000000000000000 R15: ffff9e7ead15d698
localhost kernel: FS:  0000152a3d111700(0000) GS:ffff9e855ee80000(0000) knlGS:0000000000000000
localhost kernel: CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
localhost kernel: CR2: 0000152938000010 CR3: 000000044d7a4000 CR4: 00000000003506e0
localhost kernel: Call Trace:
localhost kernel: _raw_spin_lock_irqsave+0x30/0x40
localhost kernel: remove_wait_queue+0x12/0x50
localhost kernel: kfd_wait_on_events+0x1b6/0x490 [hydcu]
localhost kernel: ? ftrace_graph_caller+0xa0/0xa0
localhost kernel: kfd_ioctl+0x38c/0x4a0 [hydcu]
localhost kernel: ? kfd_ioctl_set_trap_handler+0x70/0x70 [hydcu]
localhost kernel: ? kfd_ioctl_create_queue+0x5a0/0x5a0 [hydcu]
localhost kernel: ? ftrace_graph_caller+0xa0/0xa0
localhost kernel: __x64_sys_ioctl+0x8e/0xd0
localhost kernel: ? syscall_trace_enter.isra.18+0x143/0x1b0
localhost kernel: do_syscall_64+0x33/0x80
localhost kernel: entry_SYSCALL_64_after_hwframe+0x44/0xa9
localhost kernel: RIP: 0033:0x152a4dff68d7

Allocate the structure with kcalloc, and remove redundant 0-initialization
and a redundant loop condition check.

## References
- https://git.kernel.org/stable/c/2fece63b55c5d74cd6f5de51159e2cde37e10555
- https://git.kernel.org/stable/c/4fc8fff378b2f2039f2a666d9f8c570f4e58352c
- https://git.kernel.org/stable/c/5a3fb3b745af0ce46ec2e0c8e507bae45b937334
- https://git.kernel.org/stable/c/61f306f8df0d5559659c5578cf6d95236bcdcb25
- https://git.kernel.org/stable/c/6936525142a015e854d0a23e9ad9ea0a28b3843d
- https://git.kernel.org/stable/c/bbf5eada4334a96e3a204b2307ff5b14dc380b0b
- https://git.kernel.org/stable/c/d9923e7214a870b312bf61f6a89c7554d0966985
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53090.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
