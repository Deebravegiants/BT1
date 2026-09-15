# [H] CVE-2021-47600

## Summary
Severity: High
Advisory: CVE-2021-47600
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47600
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm btree remove: fix use after free in rebalance_children()

Move dm_tm_unlock() after dm_tm_dec().

## References
- https://git.kernel.org/stable/c/a48f6a2bf33734ec5669ee03067dfb6c5b4818d6
- https://git.kernel.org/stable/c/b03abd0aa09c05099f537cb05b8460c4298f0861
- https://git.kernel.org/stable/c/0e21e6cd5eebfc929ac5fa3b97ca2d4ace3cb6a3
- https://git.kernel.org/stable/c/1b8d2789dad0005fd5e7d35dab26a8e1203fb6da
- https://git.kernel.org/stable/c/293f957be5e39720778fb1851ced7f5fba6d51c3
- https://git.kernel.org/stable/c/501ecd90efdc9b2edc6c28852ecd098a4adf8f00
- https://git.kernel.org/stable/c/607beb420b3fe23b948a9bf447d993521a02fbbb
- https://git.kernel.org/stable/c/66ea642af6fd4eacb5d0271a922130fcf8700424
