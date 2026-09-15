# [H] x86/fpu: Ensure XFD state on signal delivery

## Summary
Severity: High
Advisory: CVE-2025-68171
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68171
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/fpu: Ensure XFD state on signal delivery

Sean reported [1] the following splat when running KVM tests:

   WARNING: CPU: 232 PID: 15391 at xfd_validate_state+0x65/0x70
   Call Trace:
    <TASK>
    fpu__clear_user_states+0x9c/0x100
    arch_do_signal_or_restart+0x142/0x210
    exit_to_user_mode_loop+0x55/0x100
    do_syscall_64+0x205/0x2c0
    entry_SYSCALL_64_after_hwframe+0x4b/0x53

Chao further identified [2] a reproducible scenario involving signal
delivery: a non-AMX task is preempted by an AMX-enabled task which
modifies the XFD MSR.

When the non-AMX task resumes and reloads XSTATE with init values,
a warning is triggered due to a mismatch between fpstate::xfd and the
CPU's current XFD state. fpu__clear_user_states() does not currently
re-synchronize the XFD state after such preemption.

Invoke xfd_update_state() which detects and corrects the mismatch if
there is a dynamic feature.

This also benefits the sigreturn path, as fpu__restore_sig() may call
fpu__clear_user_states() when the sigframe is inaccessible.

[ dhansen: minor changelog munging ]

## References
- https://git.kernel.org/stable/c/1811c610653c0cd21cc9add14595b7cffaeca511
- https://git.kernel.org/stable/c/388eff894d6bc5f921e9bfff0e4b0ab2684a96e9
- https://git.kernel.org/stable/c/3f735419c4b43cde42e6d408db39137b82474e31
- https://git.kernel.org/stable/c/5b2619b488f1d08b960c43c6468dd0759e8b3035
- https://git.kernel.org/stable/c/eefbfb722042fc9210d2e0ac2b063fd1abf51895
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68171.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68171
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
