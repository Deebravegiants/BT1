# [M] x86/i8259: Mark legacy PIC interrupts with IRQ_LEVEL

## Summary
Severity: Medium
Advisory: CVE-2023-52993
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52993
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <4.14.305, >=4.15.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/i8259: Mark legacy PIC interrupts with IRQ_LEVEL

Baoquan reported that after triggering a crash the subsequent crash-kernel
fails to boot about half of the time. It triggers a NULL pointer
dereference in the periodic tick code.

This happens because the legacy timer interrupt (IRQ0) is resent in
software which happens in soft interrupt (tasklet) context. In this context
get_irq_regs() returns NULL which leads to the NULL pointer dereference.

The reason for the resend is a spurious APIC interrupt on the IRQ0 vector
which is captured and leads to a resend when the legacy timer interrupt is
enabled. This is wrong because the legacy PIC interrupts are level
triggered and therefore should never be resent in software, but nothing
ever sets the IRQ_LEVEL flag on those interrupts, so the core code does not
know about their trigger type.

Ensure that IRQ_LEVEL is set when the legacy PCI interrupts are set up.

## References
- https://git.kernel.org/stable/c/0b08201158f177aab469e356b4d6af24fdd118df
- https://git.kernel.org/stable/c/137f1b47da5f58805da42c1b7811e28c1e353f39
- https://git.kernel.org/stable/c/496975d1a2937f4baadf3d985991b13fc4fc4f27
- https://git.kernel.org/stable/c/5fa55950729d0762a787451dc52862c3f850f859
- https://git.kernel.org/stable/c/744fe9be9665227335539b7a77ece8d9ff62b6c0
- https://git.kernel.org/stable/c/8770cd9d7c14aa99c255a0d08186f0be953e1638
- https://git.kernel.org/stable/c/e284c273dbb4c1ed68d4204bff94d0b10e4a90f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52993.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52993
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
