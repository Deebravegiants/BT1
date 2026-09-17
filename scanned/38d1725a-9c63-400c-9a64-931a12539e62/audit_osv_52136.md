# [M] CVE-2021-47112

## Summary
Severity: Medium
Advisory: CVE-2021-47112
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47112
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/kvm: Teardown PV features on boot CPU as well

Various PV features (Async PF, PV EOI, steal time) work through memory
shared with hypervisor and when we restore from hibernation we must
properly teardown all these features to make sure hypervisor doesn't
write to stale locations after we jump to the previously hibernated kernel
(which can try to place anything there). For secondary CPUs the job is
already done by kvm_cpu_down_prepare(), register syscore ops to do
the same for boot CPU.

## References
- https://git.kernel.org/stable/c/38b858da1c58ad46519a257764e059e663b59ff2
- https://git.kernel.org/stable/c/7620a669111b52f224d006dea9e1e688e2d62c54
- https://git.kernel.org/stable/c/8b79feffeca28c5459458fe78676b081e87c93a4
- https://git.kernel.org/stable/c/d1629b5b925de9b27979e929dae7fcb766daf6b6
