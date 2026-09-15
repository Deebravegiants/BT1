# [H] CVE-2022-25265

## Summary
Severity: High
Advisory: CVE-2022-25265
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2022-25265
Type: osv

## Details
In the Linux kernel through 5.16.10, certain binary files may have the exec-all attribute if they were built in approximately 2003 (e.g., with GCC 3.2.2 and Linux kernel 2.4.20). This can cause execution of bytes located in supposedly non-executable regions of a file.

## References
- https://security.netapp.com/advisory/ntap-20220318-0005/
- https://github.com/torvalds/linux/blob/1c33bb0507508af24fd754dd7123bd8e997fab2f/arch/x86/include/asm/elf.h#L281-L294
- https://github.com/x0reaxeax/exec-prot-bypass
