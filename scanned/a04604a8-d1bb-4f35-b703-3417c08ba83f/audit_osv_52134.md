# [H] CVE-2021-47110

## Summary
Severity: High
Advisory: CVE-2021-47110
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47110
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/kvm: Disable kvmclock on all CPUs on shutdown

Currenly, we disable kvmclock from machine_shutdown() hook and this
only happens for boot CPU. We need to disable it for all CPUs to
guard against memory corruption e.g. on restore from hibernate.

Note, writing '0' to kvmclock MSR doesn't clear memory location, it
just prevents hypervisor from updating the location so for the short
while after write and while CPU is still alive, the clock remains usable
and correct so we don't need to switch to some other clocksource.

## References
- https://git.kernel.org/stable/c/1df2dc09926f61319116c80ee85701df33577d70
- https://git.kernel.org/stable/c/3b0becf8b1ecf642a9edaf4c9628ffc641e490d6
- https://git.kernel.org/stable/c/9084fe1b3572664ad276f427dce575f580c9799a
- https://git.kernel.org/stable/c/c02027b5742b5aa804ef08a4a9db433295533046
