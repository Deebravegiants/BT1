# [H] KVM: x86: Ignore pending PV EOI if the vCPU has since disabled PV EOIs

## Summary
Severity: High
Advisory: CVE-2026-72284
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72284
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Ignore pending PV EOI if the vCPU has since disabled PV EOIs

Ignore KVM's internal "service pending PV EOI" request if the vCPU has
disabled PV EOIs since the request was made.  Asserting that PV EOIs are
enabled can fail if reading guest memory in pv_eoi_get_user() fails, i.e.
if pv_eoi_test_and_clr_pending() bails early, *and* the vCPU also disables
PV EOIs.

  kernel BUG at arch/x86/kvm/lapic.c:3338!
  Oops: invalid opcode: 0000 [#1] SMP
  CPU: 4 UID: 1000 PID: 890 Comm: pv_eoi_test Not tainted 7.0.0-d585aa5894d8-vm #337 PREEMPT
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
  RIP: 0010:kvm_lapic_sync_from_vapic+0x12b/0x140 [kvm]
  Call Trace:
   <TASK>
   kvm_arch_vcpu_ioctl_run+0x1075/0x1c30 [kvm]
   kvm_vcpu_ioctl+0x2d5/0x980 [kvm]
   __x64_sys_ioctl+0x8a/0xd0
   do_syscall_64+0xb5/0xb40
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
   </TASK>
  Modules linked in: kvm_intel kvm irqbypass
  ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/038b9ce6fafda1babd1e33d52cbc6039747a6d87
- https://git.kernel.org/stable/c/32bdca80aa81c2cb906f50a88b220ce1ecdc5e6e
- https://git.kernel.org/stable/c/8e9f7a95279bf608cf4c331ed89612e28c04564f
- https://git.kernel.org/stable/c/9285e4070df2c40585c3d7ec9571faa7a2b97e17
- https://git.kernel.org/stable/c/97542f15dc4cf6cd3fdc035e482dca54246ddf48
- https://git.kernel.org/stable/c/ebd7845ca0471d251a1cb48d84eb165aff5b7123
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72284.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
