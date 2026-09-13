# [H] KVM: SVM: Forcibly leave SMM mode on SHUTDOWN interception

## Summary
Severity: High
Advisory: CVE-2025-37957
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37957
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.92, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: Forcibly leave SMM mode on SHUTDOWN interception

Previously, commit ed129ec9057f ("KVM: x86: forcibly leave nested mode
on vCPU reset") addressed an issue where a triple fault occurring in
nested mode could lead to use-after-free scenarios. However, the commit
did not handle the analogous situation for System Management Mode (SMM).

This omission results in triggering a WARN when KVM forces a vCPU INIT
after SHUTDOWN interception while the vCPU is in SMM. This situation was
reprodused using Syzkaller by:

  1) Creating a KVM VM and vCPU
  2) Sending a KVM_SMI ioctl to explicitly enter SMM
  3) Executing invalid instructions causing consecutive exceptions and
     eventually a triple fault

The issue manifests as follows:

  WARNING: CPU: 0 PID: 25506 at arch/x86/kvm/x86.c:12112
  kvm_vcpu_reset+0x1d2/0x1530 arch/x86/kvm/x86.c:12112
  Modules linked in:
  CPU: 0 PID: 25506 Comm: syz-executor.0 Not tainted
  6.1.130-syzkaller-00157-g164fe5dde9b6 #0
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
  BIOS 1.12.0-1 04/01/2014
  RIP: 0010:kvm_vcpu_reset+0x1d2/0x1530 arch/x86/kvm/x86.c:12112
  Call Trace:
   <TASK>
   shutdown_interception+0x66/0xb0 arch/x86/kvm/svm/svm.c:2136
   svm_invoke_exit_handler+0x110/0x530 arch/x86/kvm/svm/svm.c:3395
   svm_handle_exit+0x424/0x920 arch/x86/kvm/svm/svm.c:3457
   vcpu_enter_guest arch/x86/kvm/x86.c:10959 [inline]
   vcpu_run+0x2c43/0x5a90 arch/x86/kvm/x86.c:11062
   kvm_arch_vcpu_ioctl_run+0x50f/0x1cf0 arch/x86/kvm/x86.c:11283
   kvm_vcpu_ioctl+0x570/0xf00 arch/x86/kvm/../../../virt/kvm/kvm_main.c:4122
   vfs_ioctl fs/ioctl.c:51 [inline]
   __do_sys_ioctl fs/ioctl.c:870 [inline]
   __se_sys_ioctl fs/ioctl.c:856 [inline]
   __x64_sys_ioctl+0x19a/0x210 fs/ioctl.c:856
   do_syscall_x64 arch/x86/entry/common.c:51 [inline]
   do_syscall_64+0x35/0x80 arch/x86/entry/common.c:81
   entry_SYSCALL_64_after_hwframe+0x6e/0xd8

Architecturally, INIT is blocked when the CPU is in SMM, hence KVM's WARN()
in kvm_vcpu_reset() to guard against KVM bugs, e.g. to detect improper
emulation of INIT.  SHUTDOWN on SVM is a weird edge case where KVM needs to
do _something_ sane with the VMCB, since it's technically undefined, and
INIT is the least awful choice given KVM's ABI.

So, double down on stuffing INIT on SHUTDOWN, and force the vCPU out of
SMM to avoid any weirdness (and the WARN).

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

[sean: massage changelog, make it clear this isn't architectural behavior]

## References
- https://git.kernel.org/stable/c/a2620f8932fa9fdabc3d78ed6efb004ca409019f
- https://git.kernel.org/stable/c/d362b21fefcef7eda8f1cd78a5925735d2b3287c
- https://git.kernel.org/stable/c/e9b28bc65fd3a56755ba503258024608292b4ab1
- https://git.kernel.org/stable/c/ec24e62a1dd3540ee696314422040180040c1e4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37957.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37957
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
