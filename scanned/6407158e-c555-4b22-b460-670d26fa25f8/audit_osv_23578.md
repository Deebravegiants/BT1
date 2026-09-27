# [H] KVM: SVM: fix panic on out-of-bounds guest IRQ

## Summary
Severity: High
Advisory: CVE-2022-49154
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49154
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: fix panic on out-of-bounds guest IRQ

As guest_irq is coming from KVM_IRQFD API call, it may trigger
crash in svm_update_pi_irte() due to out-of-bounds:

crash> bt
PID: 22218  TASK: ffff951a6ad74980  CPU: 73  COMMAND: "vcpu8"
 #0 [ffffb1ba6707fa40] machine_kexec at ffffffff8565b397
 #1 [ffffb1ba6707fa90] __crash_kexec at ffffffff85788a6d
 #2 [ffffb1ba6707fb58] crash_kexec at ffffffff8578995d
 #3 [ffffb1ba6707fb70] oops_end at ffffffff85623c0d
 #4 [ffffb1ba6707fb90] no_context at ffffffff856692c9
 #5 [ffffb1ba6707fbf8] exc_page_fault at ffffffff85f95b51
 #6 [ffffb1ba6707fc50] asm_exc_page_fault at ffffffff86000ace
    [exception RIP: svm_update_pi_irte+227]
    RIP: ffffffffc0761b53  RSP: ffffb1ba6707fd08  RFLAGS: 00010086
    RAX: ffffb1ba6707fd78  RBX: ffffb1ba66d91000  RCX: 0000000000000001
    RDX: 00003c803f63f1c0  RSI: 000000000000019a  RDI: ffffb1ba66db2ab8
    RBP: 000000000000019a   R8: 0000000000000040   R9: ffff94ca41b82200
    R10: ffffffffffffffcf  R11: 0000000000000001  R12: 0000000000000001
    R13: 0000000000000001  R14: ffffffffffffffcf  R15: 000000000000005f
    ORIG_RAX: ffffffffffffffff  CS: 0010  SS: 0018
 #7 [ffffb1ba6707fdb8] kvm_irq_routing_update at ffffffffc09f19a1 [kvm]
 #8 [ffffb1ba6707fde0] kvm_set_irq_routing at ffffffffc09f2133 [kvm]
 #9 [ffffb1ba6707fe18] kvm_vm_ioctl at ffffffffc09ef544 [kvm]
    RIP: 00007f143c36488b  RSP: 00007f143a4e04b8  RFLAGS: 00000246
    RAX: ffffffffffffffda  RBX: 00007f05780041d0  RCX: 00007f143c36488b
    RDX: 00007f05780041d0  RSI: 000000004008ae6a  RDI: 0000000000000020
    RBP: 00000000000004e8   R8: 0000000000000008   R9: 00007f05780041e0
    R10: 00007f0578004560  R11: 0000000000000246  R12: 00000000000004e0
    R13: 000000000000001a  R14: 00007f1424001c60  R15: 00007f0578003bc0
    ORIG_RAX: 0000000000000010  CS: 0033  SS: 002b

Vmx have been fix this in commit 3a8b0677fc61 (KVM: VMX: Do not BUG() on
out-of-bounds guest IRQ), so we can just copy source from that to fix
this.

## References
- https://git.kernel.org/stable/c/0fb470eb48892e131d10aa3be6915239e65758f3
- https://git.kernel.org/stable/c/3fa2d747960521a646fc1aad7aea82e95e139a68
- https://git.kernel.org/stable/c/a6ffdebfb6a9c2ffeed902b544b96fe67498210e
- https://git.kernel.org/stable/c/a80ced6ea514000d34bf1239d47553de0d1ee89e
- https://git.kernel.org/stable/c/e4d153d53d9648513481eb4ef8c212e7f1f8173d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49154.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49154
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
