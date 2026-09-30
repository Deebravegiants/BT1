# [H] CVE-2021-47226

## Summary
Severity: High
Advisory: CVE-2021-47226
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47226
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/fpu: Invalidate FPU state after a failed XRSTOR from a user buffer

Both Intel and AMD consider it to be architecturally valid for XRSTOR to
fail with #PF but nonetheless change the register state.  The actual
conditions under which this might occur are unclear [1], but it seems
plausible that this might be triggered if one sibling thread unmaps a page
and invalidates the shared TLB while another sibling thread is executing
XRSTOR on the page in question.

__fpu__restore_sig() can execute XRSTOR while the hardware registers
are preserved on behalf of a different victim task (using the
fpu_fpregs_owner_ctx mechanism), and, in theory, XRSTOR could fail but
modify the registers.

If this happens, then there is a window in which __fpu__restore_sig()
could schedule out and the victim task could schedule back in without
reloading its own FPU registers. This would result in part of the FPU
state that __fpu__restore_sig() was attempting to load leaking into the
victim task's user-visible state.

Invalidate preserved FPU registers on XRSTOR failure to prevent this
situation from corrupting any state.

[1] Frequent readers of the errata lists might imagine "complex
    microarchitectural conditions".

## References
- https://git.kernel.org/stable/c/002665dcba4bbec8c82f0aeb4bd3f44334ed2c14
- https://git.kernel.org/stable/c/a7748e021b9fb7739e3cb88449296539de0b6817
- https://git.kernel.org/stable/c/d8778e393afa421f1f117471144f8ce6deb6953a
