# [M] CVE-2021-47432

## Summary
Severity: Medium
Advisory: CVE-2021-47432
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47432
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/generic-radix-tree.c: Don't overflow in peek()

When we started spreading new inode numbers throughout most of the 64
bit inode space, that triggered some corner case bugs, in particular
some integer overflows related to the radix tree code. Oops.

## References
- https://git.kernel.org/stable/c/784d01f9bbc282abb0c5ade5beb98a87f50343ac
- https://git.kernel.org/stable/c/9492261ff2460252cf2d8de89cdf854c7e2b28a0
- https://git.kernel.org/stable/c/aa7f1827953100cdde0795289a80c6c077bfe437
- https://git.kernel.org/stable/c/ec298b958cb0c40d70c68079da933c8f31c5134c
