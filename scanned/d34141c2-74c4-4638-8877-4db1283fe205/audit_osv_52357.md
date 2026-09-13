# [M] CVE-2021-47364

## Summary
Severity: Medium
Advisory: CVE-2021-47364
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47364
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: Fix memory leak in compat_insnlist()

`compat_insnlist()` handles the 32-bit version of the `COMEDI_INSNLIST`
ioctl (whenwhen `CONFIG_COMPAT` is enabled).  It allocates memory to
temporarily hold an array of `struct comedi_insn` converted from the
32-bit version in user space.  This memory is only being freed if there
is a fault while filling the array, otherwise it is leaked.

Add a call to `kfree()` to fix the leak.

## References
- https://git.kernel.org/stable/c/8d6a21e4cd6a319b0662cbe4ad6199e276ac776a
- https://git.kernel.org/stable/c/bb509a6ffed2c8b0950f637ab5779aa818ed1596
- https://git.kernel.org/stable/c/f217b6c1e28ed0b353634ce4d92a155b80bd1671
