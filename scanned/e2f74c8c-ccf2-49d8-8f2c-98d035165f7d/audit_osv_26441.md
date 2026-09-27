# [H] arm64: efi: Make efi_rt_lock a raw_spinlock

## Summary
Severity: High
Advisory: CVE-2023-53216
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53216
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.175, >=5.11.0 <5.15.103, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: efi: Make efi_rt_lock a raw_spinlock

Running a rt-kernel base on 6.2.0-rc3-rt1 on an Ampere Altra outputs
the following:
  BUG: sleeping function called from invalid context at kernel/locking/spinlock_rt.c:46
  in_atomic(): 1, irqs_disabled(): 0, non_block: 0, pid: 9, name: kworker/u320:0
  preempt_count: 2, expected: 0
  RCU nest depth: 0, expected: 0
  3 locks held by kworker/u320:0/9:
  #0: ffff3fff8c27d128 ((wq_completion)efi_rts_wq){+.+.}-{0:0}, at: process_one_work (./include/linux/atomic/atomic-long.h:41)
  #1: ffff80000861bdd0 ((work_completion)(&efi_rts_work.work)){+.+.}-{0:0}, at: process_one_work (./include/linux/atomic/atomic-long.h:41)
  #2: ffffdf7e1ed3e460 (efi_rt_lock){+.+.}-{3:3}, at: efi_call_rts (drivers/firmware/efi/runtime-wrappers.c:101)
  Preemption disabled at:
  efi_virtmap_load (./arch/arm64/include/asm/mmu_context.h:248)
  CPU: 0 PID: 9 Comm: kworker/u320:0 Tainted: G        W          6.2.0-rc3-rt1
  Hardware name: WIWYNN Mt.Jade Server System B81.03001.0005/Mt.Jade Motherboard, BIOS 1.08.20220218 (SCP: 1.08.20220218) 2022/02/18
  Workqueue: efi_rts_wq efi_call_rts
  Call trace:
  dump_backtrace (arch/arm64/kernel/stacktrace.c:158)
  show_stack (arch/arm64/kernel/stacktrace.c:165)
  dump_stack_lvl (lib/dump_stack.c:107 (discriminator 4))
  dump_stack (lib/dump_stack.c:114)
  __might_resched (kernel/sched/core.c:10134)
  rt_spin_lock (kernel/locking/rtmutex.c:1769 (discriminator 4))
  efi_call_rts (drivers/firmware/efi/runtime-wrappers.c:101)
  [...]

This seems to come from commit ff7a167961d1 ("arm64: efi: Execute
runtime services from a dedicated stack") which adds a spinlock. This
spinlock is taken through:
efi_call_rts()
\-efi_call_virt()
  \-efi_call_virt_pointer()
    \-arch_efi_call_virt_setup()

Make 'efi_rt_lock' a raw_spinlock to avoid being preempted.

[ardb: The EFI runtime services are called with a different set of
       translation tables, and are permitted to use the SIMD registers.
       The context switch code preserves/restores neither, and so EFI
       calls must be made with preemption disabled, rather than only
       disabling migration.]

## References
- https://git.kernel.org/stable/c/030b1c4217a4f504c7d0795a2bd86b7181e56f11
- https://git.kernel.org/stable/c/0e68b5517d3767562889f1d83fdb828c26adb24f
- https://git.kernel.org/stable/c/4e8f7d998b582a99aadedd07ae6086e99b89c97a
- https://git.kernel.org/stable/c/6a72729ed6accc86dad5522895e8fa2f96642a2c
- https://git.kernel.org/stable/c/8b38969fa01662ec539a0d08a8ea5ec6f31fa4ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53216.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
