# [M] CVE-2021-47353

## Summary
Severity: Medium
Advisory: CVE-2021-47353
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47353
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Fix NULL pointer dereference in udf_symlink function

In function udf_symlink, epos.bh is assigned with the value returned
by udf_tgetblk. The function udf_tgetblk is defined in udf/misc.c
and returns the value of sb_getblk function that could be NULL.
Then, epos.bh is used without any check, causing a possible
NULL pointer dereference when sb_getblk fails.

This fix adds a check to validate the value of epos.bh.

## References
- https://git.kernel.org/stable/c/3638705ecd5ad2785e996f820121c0ad15ce64b5
- https://git.kernel.org/stable/c/5150877e4d99f85057a458daac7cd7c01005d5c6
- https://git.kernel.org/stable/c/aebed6b19e51a34003d998da5ebb1dfdd2cb1d02
- https://git.kernel.org/stable/c/21bf1414580c36ffc8d8de043beb3508cf812238
- https://git.kernel.org/stable/c/2f3d9ddd32a28803baa547e6274983b67d5e287c
- https://git.kernel.org/stable/c/371566f63cbd0bb6fbb25b8fe9d5798268d35af9
- https://git.kernel.org/stable/c/80d505aee6398cf8beb72475c7edcf1733c1c68b
- https://git.kernel.org/stable/c/baea588a42d675e35daeaddd10fbc9700550bc4d
- https://git.kernel.org/stable/c/fa236c2b2d4436d9f19ee4e5d5924e90ffd7bb43
