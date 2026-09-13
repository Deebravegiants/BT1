# [H] parisc: Fix random data corruption from exception handler

## Summary
Severity: High
Advisory: CVE-2024-26706
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26706
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: Fix random data corruption from exception handler

The current exception handler implementation, which assists when accessing
user space memory, may exhibit random data corruption if the compiler decides
to use a different register than the specified register %r29 (defined in
ASM_EXCEPTIONTABLE_REG) for the error code. If the compiler choose another
register, the fault handler will nevertheless store -EFAULT into %r29 and thus
trash whatever this register is used for.
Looking at the assembly I found that this happens sometimes in emulate_ldd().

To solve the issue, the easiest solution would be if it somehow is
possible to tell the fault handler which register is used to hold the error
code. Using %0 or %1 in the inline assembly is not posssible as it will show
up as e.g. %r29 (with the "%r" prefix), which the GNU assembler can not
convert to an integer.

This patch takes another, better and more flexible approach:
We extend the __ex_table (which is out of the execution path) by one 32-word.
In this word we tell the compiler to insert the assembler instruction
"or %r0,%r0,%reg", where %reg references the register which the compiler
choosed for the error return code.
In case of an access failure, the fault handler finds the __ex_table entry and
can examine the opcode. The used register is encoded in the lowest 5 bits, and
the fault handler can then store -EFAULT into this register.

Since we extend the __ex_table to 3 words we can't use the BUILDTIME_TABLE_SORT
config option any longer.

## References
- https://git.kernel.org/stable/c/23027309b099ffc4efca5477009a11dccbdae592
- https://git.kernel.org/stable/c/8b1d72395635af45410b66cc4c4ab37a12c4a831
- https://git.kernel.org/stable/c/ce31d79aa1f13a2345791f84935281a2c194e003
- https://git.kernel.org/stable/c/fa69a8063f8b27f3c7434a0d4f464a76a62f24d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26706.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26706
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
