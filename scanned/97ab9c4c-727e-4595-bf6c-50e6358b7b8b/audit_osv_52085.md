# [M] CVE-2021-47054

## Summary
Severity: Medium
Advisory: CVE-2021-47054
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47054
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: qcom: Put child node before return

Put child node before return to fix potential reference count leak.
Generally, the reference count of child is incremented and decremented
automatically in the macro for_each_available_child_of_node() and should
be decremented manually if the loop is broken in loop body.

## References
- https://git.kernel.org/stable/c/ac6ad7c2a862d682bb584a4bc904d89fa7721af8
- https://git.kernel.org/stable/c/c6f8e0dc8da1cd78d640dee392071cc2326ec1b2
- https://git.kernel.org/stable/c/00f6abd3509b1d70d0ab0fbe65ce5685cebed8be
- https://git.kernel.org/stable/c/3a76ec28824c01b57aa1f0927841d75e4f167cb8
- https://git.kernel.org/stable/c/6b68c03dfc79cd95a58dfd03f91f6e82829a1b0c
- https://git.kernel.org/stable/c/94810fc52925eb122a922df7f9966cf3f4ba7391
- https://git.kernel.org/stable/c/a399dd80e697a02cfb23e2fc09b87849994043d9
- https://git.kernel.org/stable/c/a6191e91c10e50bd51db65a00e03d02b6b0cf8c4
