# [H] KVM: Don't clobber irqfd routing type when deassigning irqfd

## Summary
Severity: High
Advisory: CVE-2026-23198
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23198
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.250, >=5.11.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Don't clobber irqfd routing type when deassigning irqfd

When deassigning a KVM_IRQFD, don't clobber the irqfd's copy of the IRQ's
routing entry as doing so breaks kvm_arch_irq_bypass_del_producer() on x86
and arm64, which explicitly look for KVM_IRQ_ROUTING_MSI.  Instead, to
handle a concurrent routing update, verify that the irqfd is still active
before consuming the routing information.  As evidenced by the x86 and
arm64 bugs, and another bug in kvm_arch_update_irqfd_routing() (see below),
clobbering the entry type without notifying arch code is surprising and
error prone.

As a bonus, checking that the irqfd is active provides a convenient
location for documenting _why_ KVM must not consume the routing entry for
an irqfd that is in the process of being deassigned: once the irqfd is
deleted from the list (which happens *before* the eventfd is detached), it
will no longer receive updates via kvm_irq_routing_update(), and so KVM
could deliver an event using stale routing information (relative to
KVM_SET_GSI_ROUTING returning to userspace).

As an even better bonus, explicitly checking for the irqfd being active
fixes a similar bug to the one the clobbering is trying to prevent: if an
irqfd is deactivated, and then its routing is changed,
kvm_irq_routing_update() won't invoke kvm_arch_update_irqfd_routing()
(because the irqfd isn't in the list).  And so if the irqfd is in bypass
mode, IRQs will continue to be posted using the old routing information.

As for kvm_arch_irq_bypass_del_producer(), clobbering the routing type
results in KVM incorrectly keeping the IRQ in bypass mode, which is
especially problematic on AMD as KVM tracks IRQs that are being posted to
a vCPU in a list whose lifetime is tied to the irqfd.

Without the help of KASAN to detect use-after-free, the most common
sympton on AMD is a NULL pointer deref in amd_iommu_update_ga() due to
the memory for irqfd structure being re-allocated and zeroed, resulting
in irqfd->irq_bypass_data being NULL when read by
avic_update_iommu_vcpu_affinity():

  BUG: kernel NULL pointer dereference, address: 0000000000000018
  #PF: supervisor read access in kernel mode
  #PF: error_code(0x0000) - not-present page
  PGD 40cf2b9067 P4D 40cf2b9067 PUD 408362a067 PMD 0
  Oops: Oops: 0000 [#1] SMP
  CPU: 6 UID: 0 PID: 40383 Comm: vfio_irq_test
  Tainted: G     U  W  O        6.19.0-smp--5dddc257e6b2-irqfd #31 NONE
  Tainted: [U]=USER, [W]=WARN, [O]=OOT_MODULE
  Hardware name: Google, Inc. Arcadia_IT_80/Arcadia_IT_80, BIOS 34.78.2-0 09/05/2025
  RIP: 0010:amd_iommu_update_ga+0x19/0xe0
  Call Trace:
   <TASK>
   avic_update_iommu_vcpu_affinity+0x3d/0x90 [kvm_amd]
   __avic_vcpu_load+0xf4/0x130 [kvm_amd]
   kvm_arch_vcpu_load+0x89/0x210 [kvm]
   vcpu_load+0x30/0x40 [kvm]
   kvm_arch_vcpu_ioctl_run+0x45/0x620 [kvm]
   kvm_vcpu_ioctl+0x571/0x6a0 [kvm]
   __se_sys_ioctl+0x6d/0xb0
   do_syscall_64+0x6f/0x9d0
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
  RIP: 0033:0x46893b
    </TASK>
  ---[ end trace 0000000000000000 ]---

If AVIC is inhibited when the irfd is deassigned, the bug will manifest as
list corruption, e.g. on the next irqfd assignment.

  list_add corruption. next->prev should be prev (ffff8d474d5cd588),
                       but was 0000000000000000. (next=ffff8d8658f86530).
  ------------[ cut here ]------------
  kernel BUG at lib/list_debug.c:31!
  Oops: invalid opcode: 0000 [#1] SMP
  CPU: 128 UID: 0 PID: 80818 Comm: vfio_irq_test
  Tainted: G     U  W  O        6.19.0-smp--f19dc4d680ba-irqfd #28 NONE
  Tainted: [U]=USER, [W]=WARN, [O]=OOT_MODULE
  Hardware name: Google, Inc. Arcadia_IT_80/Arcadia_IT_80, BIOS 34.78.2-0 09/05/2025
  RIP: 0010:__list_add_valid_or_report+0x97/0xc0
  Call Trace:
   <TASK>
   avic_pi_update_irte+0x28e/0x2b0 [kvm_amd]
   kvm_pi_update_irte+0xbf/0x190 [kvm]
   kvm_arch_irq_bypass_add_producer+0x72/0x90 [kvm]
   irq_bypass_register_consumer+0xcd/0x170 [irqbypa
---truncated---

## References
- https://git.kernel.org/stable/c/2284bc168b148a17b5ca3b37b3d95c411f18a08d
- https://git.kernel.org/stable/c/4385b2f2843549bfb932e0dcf76bf4b065543a3c
- https://git.kernel.org/stable/c/6d14ba1e144e796b5fc81044f08cfba9024ca195
- https://git.kernel.org/stable/c/959a063e7f12524bc1871ad1f519787967bbcd45
- https://git.kernel.org/stable/c/b4d37cdb77a0015f51fee083598fa227cc07aaf1
- https://git.kernel.org/stable/c/b61f9b2fcf181451d0a319889478cc53c001123e
- https://git.kernel.org/stable/c/ff48c9312d042bfbe826ca675e98acc6c623211c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
