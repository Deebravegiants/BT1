# [M] CVE-2017-15537

## Summary
Severity: Medium
Advisory: CVE-2017-15537
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-17
Source: https://osv.dev/vulnerability/CVE-2017-15537
Type: osv

## Details
The x86/fpu (Floating Point Unit) subsystem in the Linux kernel before 4.13.5, when a processor supports the xsave feature but not the xsaves feature, does not correctly handle attempts to set reserved bits in the xstate header via the ptrace() or rt_sigreturn() system call, allowing local users to read the FPU registers of other processes on the system, related to arch/x86/kernel/fpu/regset.c and arch/x86/kernel/fpu/signal.c.

## References
- https://source.android.com/security/bulletin/pixel/2018-01-01
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=814fb7bb7db5433757d76f4c4502c96fc53b0b5e
- https://github.com/torvalds/linux/commit/814fb7bb7db5433757d76f4c4502c96fc53b0b5e
