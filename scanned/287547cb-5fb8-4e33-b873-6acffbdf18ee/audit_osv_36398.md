# [H] KVM: x86/mmu: Drop/zap existing present SPTE even when creating an MMIO SPTE

## Summary
Severity: High
Advisory: CVE-2026-23401
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-23401
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86/mmu: Drop/zap existing present SPTE even when creating an MMIO SPTE

When installing an emulated MMIO SPTE, do so *after* dropping/zapping the
existing SPTE (if it's shadow-present).  While commit a54aa15c6bda3 was
right about it being impossible to convert a shadow-present SPTE to an
MMIO SPTE due to a _guest_ write, it failed to account for writes to guest
memory that are outside the scope of KVM.

E.g. if host userspace modifies a shadowed gPTE to switch from a memslot
to emulted MMIO and then the guest hits a relevant page fault, KVM will
install the MMIO SPTE without first zapping the shadow-present SPTE.

  ------------[ cut here ]------------
  is_shadow_present_pte(*sptep)
  WARNING: arch/x86/kvm/mmu/mmu.c:484 at mark_mmio_spte+0xb2/0xc0 [kvm], CPU#0: vmx_ept_stale_r/4292
  Modules linked in: kvm_intel kvm irqbypass
  CPU: 0 UID: 1000 PID: 4292 Comm: vmx_ept_stale_r Not tainted 7.0.0-rc2-eafebd2d2ab0-sink-vm #319 PREEMPT
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
  RIP: 0010:mark_mmio_spte+0xb2/0xc0 [kvm]
  Call Trace:
   <TASK>
   mmu_set_spte+0x237/0x440 [kvm]
   ept_page_fault+0x535/0x7f0 [kvm]
   kvm_mmu_do_page_fault+0xee/0x1f0 [kvm]
   kvm_mmu_page_fault+0x8d/0x620 [kvm]
   vmx_handle_exit+0x18c/0x5a0 [kvm_intel]
   kvm_arch_vcpu_ioctl_run+0xc55/0x1c20 [kvm]
   kvm_vcpu_ioctl+0x2d5/0x980 [kvm]
   __x64_sys_ioctl+0x8a/0xd0
   do_syscall_64+0xb5/0x730
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
  RIP: 0033:0x47fa3f
   </TASK>
  ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/20656cd1f243d3a154aac5dd1b823110b6906fe1
- https://git.kernel.org/stable/c/459158151a158a6703b49f3c9de0e536d8bd553f
- https://git.kernel.org/stable/c/695320de6eadb75aaed8be1787c4ce4c189e4c7b
- https://git.kernel.org/stable/c/aad885e774966e97b675dfe928da164214a71605
- https://git.kernel.org/stable/c/bce7fe59d43531623f3e43779127bfb33804925d
- https://git.kernel.org/stable/c/ed5909992f344a7d3f4024261e9f751d9618a27d
- https://git.kernel.org/stable/c/fd28c5618699180cd69619801e9ae6a5266c0a22
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23401.json
- https://access.redhat.com/errata/RHSA-2026:13577
- https://access.redhat.com/errata/RHSA-2026:13578
- https://access.redhat.com/errata/RHSA-2026:13932
- https://access.redhat.com/errata/RHSA-2026:13936
- https://access.redhat.com/errata/RHSA-2026:14137
- https://access.redhat.com/errata/RHSA-2026:14230
- https://access.redhat.com/errata/RHSA-2026:14339
- https://access.redhat.com/errata/RHSA-2026:15883
- https://access.redhat.com/errata/RHSA-2026:19521
- https://access.redhat.com/errata/RHSA-2026:19568
- https://access.redhat.com/errata/RHSA-2026:19569
- https://access.redhat.com/errata/RHSA-2026:19875
