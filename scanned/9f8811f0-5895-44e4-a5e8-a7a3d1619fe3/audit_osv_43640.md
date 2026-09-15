# [H] KVM: SVM: Update x2APIC MSR intercepts if AVIC is inhibited while L2 is active

## Summary
Severity: High
Advisory: CVE-2026-74516
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74516
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: Update x2APIC MSR intercepts if AVIC is inhibited while L2 is active

Always update x2APIC MSR intercepts for L1 when AVIC is deactivated, even
if L2 is active and KVM is using a separate MSR bitmap to run L2.  If AVIC
is fully enabled prior to running L2, and is then inhibited while L2 is
active (for a VM-scoped inhibit), then KVM will run L1 with AVIC disabled,
but with x2APIC MSR intercepts disabled, i.e. will allow L1 to read most of
the host's APIC state, send arbitrary interrupts, change task priority, and
ultimately trivially DoS the host.

E.g. sending a self-IPI in L1 on HYPERV_REENLIGHTENMENT_VECTOR, 0xee, with
CONFIG_HYPERV=n in the host kernel as a "safe" PoC, yields:

  Spurious interrupt (vector 0xee) on CPU#425. Acked

And hacking KVM to abuse kvm_set_posted_intr_wakeup_handler() to register a
handler and WARN on POSTED_INTR_WAKEUP_VECTOR yields:

  ------------[ cut here ]------------
  WARNING: arch/x86/kvm/svm/svm.c:5594 at pi_wakeup_handler+0x9/0x10 [kvm_amd], CPU#156: nested_x2apic_t/316940
  CPU: 156 UID: 0 PID: 316940 Comm: nested_x2apic_t Tainted: G S   U
  Tainted: [S]=CPU_OUT_OF_SPEC, [U]=USER
  Hardware name: Google Astoria-Turin/astoria, BIOS 0.20260209.0-0 02/09/2026
  RIP: 0010:pi_wakeup_handler+0x9/0x10 [kvm_amd]
  Call Trace:
   <IRQ>
   sysvec_kvm_posted_intr_wakeup_ipi+0x64/0x80
   </IRQ>
   <TASK>
   asm_sysvec_kvm_posted_intr_wakeup_ipi+0x1a/0x20
  RIP: 0010:vcpu_run+0x1430/0x1e40 [kvm]
   kvm_arch_vcpu_ioctl_run+0x2c1/0x600 [kvm]
   kvm_vcpu_ioctl+0x580/0x6b0 [kvm]
   __se_sys_ioctl+0x6d/0xb0
   do_syscall_64+0x10a/0x480
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
  RIP: 0033:0x46ff4b
   </TASK>
  ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/4ca05385b3ddbd463be17c6d69ec76fca657081d
- https://git.kernel.org/stable/c/6664a5aea45318f4ec156a729949b474dd6e3159
- https://git.kernel.org/stable/c/7668c58dcf465559dc7a0d2e95e9cb79cf47454b
- https://git.kernel.org/stable/c/7d3aae206663c4e006b25a1c7a20a4029e67da76
- https://git.kernel.org/stable/c/89f9e8398e79c49886766fc24a84c37726231104
- https://git.kernel.org/stable/c/f12373625b4dc9bcc89c41872648878c73bb9272
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74516.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74516
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
