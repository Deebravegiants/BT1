# [M] CVE-2021-47018

## Summary
Severity: Medium
Advisory: CVE-2021-47018
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47018
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/64: Fix the definition of the fixmap area

At the time being, the fixmap area is defined at the top of
the address space or just below KASAN.

This definition is not valid for PPC64.

For PPC64, use the top of the I/O space.

Because of circular dependencies, it is not possible to include
asm/fixmap.h in asm/book3s/64/pgtable.h , so define a fixed size
AREA at the top of the I/O space for fixmap and ensure during
build that the size is big enough.

## References
- https://git.kernel.org/stable/c/4b9fb2c9039a206d37f215936a4d5bee7b1bf9cd
- https://git.kernel.org/stable/c/9ccba66d4d2aff9a3909aa77d57ea8b7cc166f3c
- https://git.kernel.org/stable/c/a84df7c80bdac598d6ac9268ae578da6928883e8
- https://git.kernel.org/stable/c/abb07dc5e8b61ab7b1dde20dd73aa01a3aeb183f
