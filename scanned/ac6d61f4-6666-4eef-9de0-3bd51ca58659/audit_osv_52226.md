# [M] CVE-2021-47217

## Summary
Severity: Medium
Advisory: CVE-2021-47217
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47217
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/hyperv: Fix NULL deref in set_hv_tscchange_cb() if Hyper-V setup fails

Check for a valid hv_vp_index array prior to derefencing hv_vp_index when
setting Hyper-V's TSC change callback.  If Hyper-V setup failed in
hyperv_init(), the kernel will still report that it's running under
Hyper-V, but will have silently disabled nearly all functionality.

  BUG: kernel NULL pointer dereference, address: 0000000000000010
  #PF: supervisor read access in kernel mode
  #PF: error_code(0x0000) - not-present page
  PGD 0 P4D 0
  Oops: 0000 [#1] SMP
  CPU: 4 PID: 1 Comm: swapper/0 Not tainted 5.15.0-rc2+ #75
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
  RIP: 0010:set_hv_tscchange_cb+0x15/0xa0
  Code: <8b> 04 82 8b 15 12 17 85 01 48 c1 e0 20 48 0d ee 00 01 00 f6 c6 08
  ...
  Call Trace:
   kvm_arch_init+0x17c/0x280
   kvm_init+0x31/0x330
   vmx_init+0xba/0x13a
   do_one_initcall+0x41/0x1c0
   kernel_init_freeable+0x1f2/0x23b
   kernel_init+0x16/0x120
   ret_from_fork+0x22/0x30

## References
- https://git.kernel.org/stable/c/b20ec58f8a6f4fef32cc71480ddf824584e24743
- https://git.kernel.org/stable/c/daf972118c517b91f74ff1731417feb4270625a4
- https://git.kernel.org/stable/c/8823ea27fff6084bbb4bc71d15378fae0220b1d8
- https://git.kernel.org/stable/c/9c177eee116cf888276d3748cb176e72562cfd5c
- https://git.kernel.org/stable/c/b0e44dfb4e4c699cca33ede431b8d127e6e8d661
