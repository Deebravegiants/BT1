# [H] KVM: Always flush async #PF workqueue when vCPU is being destroyed

## Summary
Severity: High
Advisory: CVE-2024-26976
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26976
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Always flush async #PF workqueue when vCPU is being destroyed

Always flush the per-vCPU async #PF workqueue when a vCPU is clearing its
completion queue, e.g. when a VM and all its vCPUs is being destroyed.
KVM must ensure that none of its workqueue callbacks is running when the
last reference to the KVM _module_ is put.  Gifting a reference to the
associated VM prevents the workqueue callback from dereferencing freed
vCPU/VM memory, but does not prevent the KVM module from being unloaded
before the callback completes.

Drop the misguided VM refcount gifting, as calling kvm_put_kvm() from
async_pf_execute() if kvm_put_kvm() flushes the async #PF workqueue will
result in deadlock.  async_pf_execute() can't return until kvm_put_kvm()
finishes, and kvm_put_kvm() can't return until async_pf_execute() finishes:

 WARNING: CPU: 8 PID: 251 at virt/kvm/kvm_main.c:1435 kvm_put_kvm+0x2d/0x320 [kvm]
 Modules linked in: vhost_net vhost vhost_iotlb tap kvm_intel kvm irqbypass
 CPU: 8 PID: 251 Comm: kworker/8:1 Tainted: G        W          6.6.0-rc1-e7af8d17224a-x86/gmem-vm #119
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
 Workqueue: events async_pf_execute [kvm]
 RIP: 0010:kvm_put_kvm+0x2d/0x320 [kvm]
 Call Trace:
  <TASK>
  async_pf_execute+0x198/0x260 [kvm]
  process_one_work+0x145/0x2d0
  worker_thread+0x27e/0x3a0
  kthread+0xba/0xe0
  ret_from_fork+0x2d/0x50
  ret_from_fork_asm+0x11/0x20
  </TASK>
 ---[ end trace 0000000000000000 ]---
 INFO: task kworker/8:1:251 blocked for more than 120 seconds.
       Tainted: G        W          6.6.0-rc1-e7af8d17224a-x86/gmem-vm #119
 "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
 task:kworker/8:1     state:D stack:0     pid:251   ppid:2      flags:0x00004000
 Workqueue: events async_pf_execute [kvm]
 Call Trace:
  <TASK>
  __schedule+0x33f/0xa40
  schedule+0x53/0xc0
  schedule_timeout+0x12a/0x140
  __wait_for_common+0x8d/0x1d0
  __flush_work.isra.0+0x19f/0x2c0
  kvm_clear_async_pf_completion_queue+0x129/0x190 [kvm]
  kvm_arch_destroy_vm+0x78/0x1b0 [kvm]
  kvm_put_kvm+0x1c1/0x320 [kvm]
  async_pf_execute+0x198/0x260 [kvm]
  process_one_work+0x145/0x2d0
  worker_thread+0x27e/0x3a0
  kthread+0xba/0xe0
  ret_from_fork+0x2d/0x50
  ret_from_fork_asm+0x11/0x20
  </TASK>

If kvm_clear_async_pf_completion_queue() actually flushes the workqueue,
then there's no need to gift async_pf_execute() a reference because all
invocations of async_pf_execute() will be forced to complete before the
vCPU and its VM are destroyed/freed.  And that in turn fixes the module
unloading bug as __fput() won't do module_put() on the last vCPU reference
until the vCPU has been freed, e.g. if closing the vCPU file also puts the
last reference to the KVM module.

Note that kvm_check_async_pf_completion() may also take the work item off
the completion queue and so also needs to flush the work queue, as the
work will not be seen by kvm_clear_async_pf_completion_queue().  Waiting
on the workqueue could theoretically delay a vCPU due to waiting for the
work to complete, but that's a very, very small chance, and likely a very
small delay.  kvm_arch_async_page_present_queued() unconditionally makes a
new request, i.e. will effectively delay entering the guest, so the
remaining work is really just:

        trace_kvm_async_pf_completed(addr, cr2_or_gpa);

        __kvm_vcpu_wake_up(vcpu);

        mmput(mm);

and mmput() can't drop the last reference to the page tables if the vCPU is
still alive, i.e. the vCPU won't get stuck tearing down page tables.

Add a helper to do the flushing, specifically to deal with "wakeup all"
work items, as they aren't actually work items, i.e. are never placed in a
workqueue.  Trying to flush a bogus workqueue entry rightly makes
__flush_work() complain (kudos to whoever added that sanity check).

Note, commit 5f6de5cbebee ("KVM: Prevent module exit until al
---truncated---

## References
- https://git.kernel.org/stable/c/3d75b8aa5c29058a512db29da7cbee8052724157
- https://git.kernel.org/stable/c/4f3a3bce428fb439c66a578adc447afce7b4a750
- https://git.kernel.org/stable/c/82e25cc1c2e93c3023da98be282322fc08b61ffb
- https://git.kernel.org/stable/c/83d3c5e309611ef593e2fcb78444fc8ceedf9bac
- https://git.kernel.org/stable/c/a75afe480d4349c524d9c659b1a5a544dbc39a98
- https://git.kernel.org/stable/c/ab2c2f5d9576112ad22cfd3798071cb74693b1f5
- https://git.kernel.org/stable/c/b54478d20375874aeee257744dedfd3e413432ff
- https://git.kernel.org/stable/c/caa9af2e27c275e089d702cfbaaece3b42bca31b
- https://git.kernel.org/stable/c/f8730d6335e5f43d09151fca1f0f41922209a264
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26976.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26976
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
