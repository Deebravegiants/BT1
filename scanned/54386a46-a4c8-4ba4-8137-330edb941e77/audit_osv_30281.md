# [H] arm64/sve: Discard stale CPU state when handling SVE traps

## Summary
Severity: High
Advisory: CVE-2024-50275
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50275
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64/sve: Discard stale CPU state when handling SVE traps

The logic for handling SVE traps manipulates saved FPSIMD/SVE state
incorrectly, and a race with preemption can result in a task having
TIF_SVE set and TIF_FOREIGN_FPSTATE clear even though the live CPU state
is stale (e.g. with SVE traps enabled). This has been observed to result
in warnings from do_sve_acc() where SVE traps are not expected while
TIF_SVE is set:

|         if (test_and_set_thread_flag(TIF_SVE))
|                 WARN_ON(1); /* SVE access shouldn't have trapped */

Warnings of this form have been reported intermittently, e.g.

  https://lore.kernel.org/linux-arm-kernel/CA+G9fYtEGe_DhY2Ms7+L7NKsLYUomGsgqpdBj+QwDLeSg=JhGg@mail.gmail.com/
  https://lore.kernel.org/linux-arm-kernel/000000000000511e9a060ce5a45c@google.com/

The race can occur when the SVE trap handler is preempted before and
after manipulating the saved FPSIMD/SVE state, starting and ending on
the same CPU, e.g.

| void do_sve_acc(unsigned long esr, struct pt_regs *regs)
| {
|         // Trap on CPU 0 with TIF_SVE clear, SVE traps enabled
|         // task->fpsimd_cpu is 0.
|         // per_cpu_ptr(&fpsimd_last_state, 0) is task.
|
|         ...
|
|         // Preempted; migrated from CPU 0 to CPU 1.
|         // TIF_FOREIGN_FPSTATE is set.
|
|         get_cpu_fpsimd_context();
|
|         if (test_and_set_thread_flag(TIF_SVE))
|                 WARN_ON(1); /* SVE access shouldn't have trapped */
|
|         sve_init_regs() {
|                 if (!test_thread_flag(TIF_FOREIGN_FPSTATE)) {
|                         ...
|                 } else {
|                         fpsimd_to_sve(current);
|                         current->thread.fp_type = FP_STATE_SVE;
|                 }
|         }
|
|         put_cpu_fpsimd_context();
|
|         // Preempted; migrated from CPU 1 to CPU 0.
|         // task->fpsimd_cpu is still 0
|         // If per_cpu_ptr(&fpsimd_last_state, 0) is still task then:
|         // - Stale HW state is reused (with SVE traps enabled)
|         // - TIF_FOREIGN_FPSTATE is cleared
|         // - A return to userspace skips HW state restore
| }

Fix the case where the state is not live and TIF_FOREIGN_FPSTATE is set
by calling fpsimd_flush_task_state() to detach from the saved CPU
state. This ensures that a subsequent context switch will not reuse the
stale CPU state, and will instead set TIF_FOREIGN_FPSTATE, forcing the
new state to be reloaded from memory prior to a return to userspace.

## References
- https://git.kernel.org/stable/c/51d11ea0250d6ee461987403bbfd4b2abb5613a7
- https://git.kernel.org/stable/c/51d3d80a6dc314982a9a0aeb0961085922a1aa15
- https://git.kernel.org/stable/c/751ecf6afd6568adc98f2a6052315552c0483d18
- https://git.kernel.org/stable/c/de529504b3274d57caf8f66800b714b0d3ee235a
- https://git.kernel.org/stable/c/fa9ce027b3ce37a2bb173bf2553b5caa438fd8c9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50275.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
