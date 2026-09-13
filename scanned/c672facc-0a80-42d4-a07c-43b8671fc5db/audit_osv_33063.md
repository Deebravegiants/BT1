# [H] arm64/entry: Mask DAIF in cpu_switch_to(), call_on_irq_stack()

## Summary
Severity: High
Advisory: CVE-2025-38670
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38670
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.210, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.101, >=6.3.0 <6.12.41, >=6.7.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64/entry: Mask DAIF in cpu_switch_to(), call_on_irq_stack()

`cpu_switch_to()` and `call_on_irq_stack()` manipulate SP to change
to different stacks along with the Shadow Call Stack if it is enabled.
Those two stack changes cannot be done atomically and both functions
can be interrupted by SErrors or Debug Exceptions which, though unlikely,
is very much broken : if interrupted, we can end up with mismatched stacks
and Shadow Call Stack leading to clobbered stacks.

In `cpu_switch_to()`, it can happen when SP_EL0 points to the new task,
but x18 stills points to the old task's SCS. When the interrupt handler
tries to save the task's SCS pointer, it will save the old task
SCS pointer (x18) into the new task struct (pointed to by SP_EL0),
clobbering it.

In `call_on_irq_stack()`, it can happen when switching from the task stack
to the IRQ stack and when switching back. In both cases, we can be
interrupted when the SCS pointer points to the IRQ SCS, but SP points to
the task stack. The nested interrupt handler pushes its return addresses
on the IRQ SCS. It then detects that SP points to the task stack,
calls `call_on_irq_stack()` and clobbers the task SCS pointer with
the IRQ SCS pointer, which it will also use !

This leads to tasks returning to addresses on the wrong SCS,
or even on the IRQ SCS, triggering kernel panics via CONFIG_VMAP_STACK
or FPAC if enabled.

This is possible on a default config, but unlikely.
However, when enabling CONFIG_ARM64_PSEUDO_NMI, DAIF is unmasked and
instead the GIC is responsible for filtering what interrupts the CPU
should receive based on priority.
Given the goal of emulating NMIs, pseudo-NMIs can be received by the CPU
even in `cpu_switch_to()` and `call_on_irq_stack()`, possibly *very*
frequently depending on the system configuration and workload, leading
to unpredictable kernel panics.

Completely mask DAIF in `cpu_switch_to()` and restore it when returning.
Do the same in `call_on_irq_stack()`, but restore and mask around
the branch.
Mask DAIF even if CONFIG_SHADOW_CALL_STACK is not enabled for consistency
of behaviour between all configurations.

Introduce and use an assembly macro for saving and masking DAIF,
as the existing one saves but only masks IF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/0f67015d72627bad72da3c2084352e0aa134416b
- https://git.kernel.org/stable/c/407047893a64399f2d2390ff35cc6061107d805d
- https://git.kernel.org/stable/c/708fd522b86d2a9544c34ec6a86fa3fc23336525
- https://git.kernel.org/stable/c/9433a5f437b0948d6a2d8a02ad7a42ab7ca27a61
- https://git.kernel.org/stable/c/a6b0cb523eaa01efe8a3f76ced493ba60674c6e6
- https://git.kernel.org/stable/c/d42e6c20de6192f8e4ab4cf10be8c694ef27e8cb
- https://git.kernel.org/stable/c/f7e0231eeaa33245c649fac0303cf97209605446
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38670.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
