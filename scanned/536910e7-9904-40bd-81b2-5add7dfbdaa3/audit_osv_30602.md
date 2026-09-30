# [M] svcrdma: fix miss destroy percpu_counter in svc_rdma_proc_init()

## Summary
Severity: Medium
Advisory: CVE-2024-53215
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53215
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

svcrdma: fix miss destroy percpu_counter in svc_rdma_proc_init()

There's issue as follows:
RPC: Registered rdma transport module.
RPC: Registered rdma backchannel transport module.
RPC: Unregistered rdma transport module.
RPC: Unregistered rdma backchannel transport module.
BUG: unable to handle page fault for address: fffffbfff80c609a
PGD 123fee067 P4D 123fee067 PUD 123fea067 PMD 10c624067 PTE 0
Oops: Oops: 0000 [#1] PREEMPT SMP KASAN NOPTI
RIP: 0010:percpu_counter_destroy_many+0xf7/0x2a0
Call Trace:
 <TASK>
 __die+0x1f/0x70
 page_fault_oops+0x2cd/0x860
 spurious_kernel_fault+0x36/0x450
 do_kern_addr_fault+0xca/0x100
 exc_page_fault+0x128/0x150
 asm_exc_page_fault+0x26/0x30
 percpu_counter_destroy_many+0xf7/0x2a0
 mmdrop+0x209/0x350
 finish_task_switch.isra.0+0x481/0x840
 schedule_tail+0xe/0xd0
 ret_from_fork+0x23/0x80
 ret_from_fork_asm+0x1a/0x30
 </TASK>

If register_sysctl() return NULL, then svc_rdma_proc_cleanup() will not
destroy the percpu counters which init in svc_rdma_proc_init().
If CONFIG_HOTPLUG_CPU is enabled, residual nodes may be in the
'percpu_counters' list. The above issue may occur once the module is
removed. If the CONFIG_HOTPLUG_CPU configuration is not enabled, memory
leakage occurs.
To solve above issue just destroy all percpu counters when
register_sysctl() return NULL.

## References
- https://git.kernel.org/stable/c/1c9a99c89e45b22eb556fd2f3f729f2683f247d5
- https://git.kernel.org/stable/c/20322edcbad82a60321a8615a99ca73a9611115f
- https://git.kernel.org/stable/c/94d2d6d398706ab7218a26d61e12919c4b498e09
- https://git.kernel.org/stable/c/a12c897adf40b6e2b4a56e6912380c31bd7b2479
- https://git.kernel.org/stable/c/ce89e742a4c12b20f09a43fec1b21db33f2166cd
- https://git.kernel.org/stable/c/ebf47215d46992caea660ec01cd618005d9e687a
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53215.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
