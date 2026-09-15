# [M] LoongArch: KVM: Mark hrtimer to expire in hard interrupt context

## Summary
Severity: Medium
Advisory: CVE-2024-53089
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53089
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Mark hrtimer to expire in hard interrupt context

Like commit 2c0d278f3293f ("KVM: LAPIC: Mark hrtimer to expire in hard
interrupt context") and commit 9090825fa9974 ("KVM: arm/arm64: Let the
timer expire in hardirq context on RT"), On PREEMPT_RT enabled kernels
unmarked hrtimers are moved into soft interrupt expiry mode by default.
Then the timers are canceled from an preempt-notifier which is invoked
with disabled preemption which is not allowed on PREEMPT_RT.

The timer callback is short so in could be invoked in hard-IRQ context.
So let the timer expire on hard-IRQ context even on -RT.

This fix a "scheduling while atomic" bug for PREEMPT_RT enabled kernels:

 BUG: scheduling while atomic: qemu-system-loo/1011/0x00000002
 Modules linked in: amdgpu rfkill nft_fib_inet nft_fib_ipv4 nft_fib_ipv6 nft_fib nft_reject_inet nf_reject_ipv4 nf_reject_ipv6 nft_reject nft_ct nft_chain_nat ns
 CPU: 1 UID: 0 PID: 1011 Comm: qemu-system-loo Tainted: G        W          6.12.0-rc2+ #1774
 Tainted: [W]=WARN
 Hardware name: Loongson Loongson-3A5000-7A1000-1w-CRB/Loongson-LS3A5000-7A1000-1w-CRB, BIOS vUDK2018-LoongArch-V2.0.0-prebeta9 10/21/2022
 Stack : ffffffffffffffff 0000000000000000 9000000004e3ea38 9000000116744000
         90000001167475a0 0000000000000000 90000001167475a8 9000000005644830
         90000000058dc000 90000000058dbff8 9000000116747420 0000000000000001
         0000000000000001 6a613fc938313980 000000000790c000 90000001001c1140
         00000000000003fe 0000000000000001 000000000000000d 0000000000000003
         0000000000000030 00000000000003f3 000000000790c000 9000000116747830
         90000000057ef000 0000000000000000 9000000005644830 0000000000000004
         0000000000000000 90000000057f4b58 0000000000000001 9000000116747868
         900000000451b600 9000000005644830 9000000003a13998 0000000010000020
         00000000000000b0 0000000000000004 0000000000000000 0000000000071c1d
         ...
 Call Trace:
 [<9000000003a13998>] show_stack+0x38/0x180
 [<9000000004e3ea34>] dump_stack_lvl+0x84/0xc0
 [<9000000003a71708>] __schedule_bug+0x48/0x60
 [<9000000004e45734>] __schedule+0x1114/0x1660
 [<9000000004e46040>] schedule_rtlock+0x20/0x60
 [<9000000004e4e330>] rtlock_slowlock_locked+0x3f0/0x10a0
 [<9000000004e4f038>] rt_spin_lock+0x58/0x80
 [<9000000003b02d68>] hrtimer_cancel_wait_running+0x68/0xc0
 [<9000000003b02e30>] hrtimer_cancel+0x70/0x80
 [<ffff80000235eb70>] kvm_restore_timer+0x50/0x1a0 [kvm]
 [<ffff8000023616c8>] kvm_arch_vcpu_load+0x68/0x2a0 [kvm]
 [<ffff80000234c2d4>] kvm_sched_in+0x34/0x60 [kvm]
 [<9000000003a749a0>] finish_task_switch.isra.0+0x140/0x2e0
 [<9000000004e44a70>] __schedule+0x450/0x1660
 [<9000000004e45cb0>] schedule+0x30/0x180
 [<ffff800002354c70>] kvm_vcpu_block+0x70/0x120 [kvm]
 [<ffff800002354d80>] kvm_vcpu_halt+0x60/0x3e0 [kvm]
 [<ffff80000235b194>] kvm_handle_gspr+0x3f4/0x4e0 [kvm]
 [<ffff80000235f548>] kvm_handle_exit+0x1c8/0x260 [kvm]

## References
- https://git.kernel.org/stable/c/1e4c384a4be9ed1e069e24f388ab2ee9951b77b5
- https://git.kernel.org/stable/c/73adbd92f3223dc0c3506822b71c6b259d5d537b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53089.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
