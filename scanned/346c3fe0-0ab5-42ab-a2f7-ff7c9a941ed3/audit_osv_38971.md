# [H] KVM: x86: Add SRCU protection for reading PDPTRs in __get_sregs2()

## Summary
Severity: High
Advisory: CVE-2026-43214
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43214
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Add SRCU protection for reading PDPTRs in __get_sregs2()

Add SRCU read-side protection when reading PDPTR registers in
__get_sregs2().

Reading PDPTRs may trigger access to guest memory:
kvm_pdptr_read() -> svm_cache_reg() -> load_pdptrs() ->
kvm_vcpu_read_guest_page() -> kvm_vcpu_gfn_to_memslot()

kvm_vcpu_gfn_to_memslot() dereferences memslots via __kvm_memslots(),
which uses srcu_dereference_check() and requires either kvm->srcu or
kvm->slots_lock to be held. Currently only vcpu->mutex is held,
triggering lockdep warning:

=============================
WARNING: suspicious RCU usage in kvm_vcpu_gfn_to_memslot
6.12.59+ #3 Not tainted

include/linux/kvm_host.h:1062 suspicious rcu_dereference_check() usage!

other info that might help us debug this:

rcu_scheduler_active = 2, debug_locks = 1
1 lock held by syz.5.1717/15100:
 #0: ff1100002f4b00b0 (&vcpu->mutex){+.+.}-{3:3}, at: kvm_vcpu_ioctl+0x1d5/0x1590

Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0xf0/0x120 lib/dump_stack.c:120
 lockdep_rcu_suspicious+0x1e3/0x270 kernel/locking/lockdep.c:6824
 __kvm_memslots include/linux/kvm_host.h:1062 [inline]
 __kvm_memslots include/linux/kvm_host.h:1059 [inline]
 kvm_vcpu_memslots include/linux/kvm_host.h:1076 [inline]
 kvm_vcpu_gfn_to_memslot+0x518/0x5e0 virt/kvm/kvm_main.c:2617
 kvm_vcpu_read_guest_page+0x27/0x50 virt/kvm/kvm_main.c:3302
 load_pdptrs+0xff/0x4b0 arch/x86/kvm/x86.c:1065
 svm_cache_reg+0x1c9/0x230 arch/x86/kvm/svm/svm.c:1688
 kvm_pdptr_read arch/x86/kvm/kvm_cache_regs.h:141 [inline]
 __get_sregs2 arch/x86/kvm/x86.c:11784 [inline]
 kvm_arch_vcpu_ioctl+0x3e20/0x4aa0 arch/x86/kvm/x86.c:6279
 kvm_vcpu_ioctl+0x856/0x1590 virt/kvm/kvm_main.c:4663
 vfs_ioctl fs/ioctl.c:51 [inline]
 __do_sys_ioctl fs/ioctl.c:907 [inline]
 __se_sys_ioctl fs/ioctl.c:893 [inline]
 __x64_sys_ioctl+0x18b/0x210 fs/ioctl.c:893
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xbd/0x1d0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/57536ff0a6bd69a5808d682925202babdb5ddc13
- https://git.kernel.org/stable/c/708e20c66b2761d878a2bc3c7534e7f814e4dec5
- https://git.kernel.org/stable/c/95d848dc7e639988dbb385a8cba9b484607cf98c
- https://git.kernel.org/stable/c/9f2bfea51151dfbb24b52f452eb3d5f5fe0e506e
- https://git.kernel.org/stable/c/b33f8d816950b10e7879cd8ffd7ae4b649ada4db
- https://git.kernel.org/stable/c/f621ca24f9f489e226e22560761b04884984133b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43214.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43214
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
