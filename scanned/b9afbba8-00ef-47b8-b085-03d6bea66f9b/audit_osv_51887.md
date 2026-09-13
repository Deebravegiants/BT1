# [H] CVE-2021-4440

## Summary
Severity: High
Advisory: CVE-2021-4440
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2021-4440
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/xen: Drop USERGS_SYSRET64 paravirt call

commit afd30525a659ac0ae0904f0cb4a2ca75522c3123 upstream.

USERGS_SYSRET64 is used to return from a syscall via SYSRET, but
a Xen PV guest will nevertheless use the IRET hypercall, as there
is no sysret PV hypercall defined.

So instead of testing all the prerequisites for doing a sysret and
then mangling the stack for Xen PV again for doing an iret just use
the iret exit from the beginning.

This can easily be done via an ALTERNATIVE like it is done for the
sysenter compat case already.

It should be noted that this drops the optimization in Xen for not
restoring a few registers when returning to user mode, but it seems
as if the saved instructions in the kernel more than compensate for
this drop (a kernel build in a Xen PV guest was slightly faster with
this patch applied).

While at it remove the stale sysret32 remnants.

  [ pawan: Brad Spengler and Salvatore Bonaccorso <carnil@debian.org>
	   reported a problem with the 5.10 backport commit edc702b4a820
	   ("x86/entry_64: Add VERW just before userspace transition").

	   When CONFIG_PARAVIRT_XXL=y, CLEAR_CPU_BUFFERS is not executed in
	   syscall_return_via_sysret path as USERGS_SYSRET64 is runtime
	   patched to:

	.cpu_usergs_sysret64    = { 0x0f, 0x01, 0xf8,
				    0x48, 0x0f, 0x07 }, // swapgs; sysretq

	   which is missing CLEAR_CPU_BUFFERS. It turns out dropping
	   USERGS_SYSRET64 simplifies the code, allowing CLEAR_CPU_BUFFERS
	   to be explicitly added to syscall_return_via_sysret path. Below
	   is with CONFIG_PARAVIRT_XXL=y and this patch applied:

	   syscall_return_via_sysret:
	   ...
	   <+342>:   swapgs
	   <+345>:   xchg   %ax,%ax
	   <+347>:   verw   -0x1a2(%rip)  <------
	   <+354>:   sysretq
  ]

## References
- https://git.kernel.org/stable/c/1424ab4bb386df9cc590c73afa55f13e9b00dea2
- https://grsecurity.net/cve-2021-4440_linux_cna_case_study
