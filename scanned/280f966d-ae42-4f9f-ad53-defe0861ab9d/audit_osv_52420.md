# [M] CVE-2021-47429

## Summary
Severity: Medium
Advisory: CVE-2021-47429
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47429
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/64s: Fix unrecoverable MCE calling async handler from NMI

The machine check handler is not considered NMI on 64s. The early
handler is the true NMI handler, and then it schedules the
machine_check_exception handler to run when interrupts are enabled.

This works fine except the case of an unrecoverable MCE, where the true
NMI is taken when MSR[RI] is clear, it can not recover, so it calls
machine_check_exception directly so something might be done about it.

Calling an async handler from NMI context can result in irq state and
other things getting corrupted. This can also trigger the BUG at
  arch/powerpc/include/asm/interrupt.h:168
  BUG_ON(!arch_irq_disabled_regs(regs) && !(regs->msr & MSR_EE));

Fix this by making an _async version of the handler which is called
in the normal case, and a NMI version that is called for unrecoverable
interrupts.

## References
- https://git.kernel.org/stable/c/f08fb25bc66986b0952724530a640d9970fa52c1
- https://git.kernel.org/stable/c/d7a8e38999fbd6910516e44cb43f9f4317e54f73
