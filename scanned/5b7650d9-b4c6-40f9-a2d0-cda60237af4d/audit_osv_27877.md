# [M] arm64: entry: fix ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD

## Summary
Severity: Medium
Advisory: CVE-2024-26670
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26670
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: entry: fix ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD

Currently the ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD workaround isn't
quite right, as it is supposed to be applied after the last explicit
memory access, but is immediately followed by an LDR.

The ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD workaround is used to
handle Cortex-A520 erratum 2966298 and Cortex-A510 erratum 3117295,
which are described in:

* https://developer.arm.com/documentation/SDEN2444153/0600/?lang=en
* https://developer.arm.com/documentation/SDEN1873361/1600/?lang=en

In both cases the workaround is described as:

| If pagetable isolation is disabled, the context switch logic in the
| kernel can be updated to execute the following sequence on affected
| cores before exiting to EL0, and after all explicit memory accesses:
|
| 1. A non-shareable TLBI to any context and/or address, including
|    unused contexts or addresses, such as a `TLBI VALE1 Xzr`.
|
| 2. A DSB NSH to guarantee completion of the TLBI.

The important part being that the TLBI+DSB must be placed "after all
explicit memory accesses".

Unfortunately, as-implemented, the TLBI+DSB is immediately followed by
an LDR, as we have:

| alternative_if ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD
| 	tlbi	vale1, xzr
| 	dsb	nsh
| alternative_else_nop_endif
| alternative_if_not ARM64_UNMAP_KERNEL_AT_EL0
| 	ldr	lr, [sp, #S_LR]
| 	add	sp, sp, #PT_REGS_SIZE		// restore sp
| 	eret
| alternative_else_nop_endif
|
| [ ... KPTI exception return path ... ]

This patch fixes this by reworking the logic to place the TLBI+DSB
immediately before the ERET, after all explicit memory accesses.

The ERET is currently in a separate alternative block, and alternatives
cannot be nested. To account for this, the alternative block for
ARM64_UNMAP_KERNEL_AT_EL0 is replaced with a single alternative branch
to skip the KPTI logic, with the new shape of the logic being:

| alternative_insn "b .L_skip_tramp_exit_\@", nop, ARM64_UNMAP_KERNEL_AT_EL0
| 	[ ... KPTI exception return path ... ]
| .L_skip_tramp_exit_\@:
|
| 	ldr	lr, [sp, #S_LR]
| 	add	sp, sp, #PT_REGS_SIZE		// restore sp
|
| alternative_if ARM64_WORKAROUND_SPECULATIVE_UNPRIV_LOAD
| 	tlbi	vale1, xzr
| 	dsb	nsh
| alternative_else_nop_endif
| 	eret

The new structure means that the workaround is only applied when KPTI is
not in use; this is fine as noted in the documented implications of the
erratum:

| Pagetable isolation between EL0 and higher level ELs prevents the
| issue from occurring.

... and as per the workaround description quoted above, the workaround
is only necessary "If pagetable isolation is disabled".

## References
- https://git.kernel.org/stable/c/58eb5c07f41704464b9acc09ab0707b6769db6c0
- https://git.kernel.org/stable/c/832dd634bd1b4e3bbe9f10b9c9ba5db6f6f2b97f
- https://git.kernel.org/stable/c/baa0aaac16432019651e0d60c41cd34a0c3c3477
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26670.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
