# [H] CVE-2021-47204

## Summary
Severity: High
Advisory: CVE-2021-47204
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47204
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dpaa2-eth: fix use-after-free in dpaa2_eth_remove

Access to netdev after free_netdev() will cause use-after-free bug.
Move debug log before free_netdev() call to avoid it.

## References
- https://git.kernel.org/stable/c/32d4686224744819ddcae58b666c21d2a4ef4c88
- https://git.kernel.org/stable/c/9b5a333272a48c2f8b30add7a874e46e8b26129c
- https://git.kernel.org/stable/c/d74ff10ed2d93dc9b67e99a74b36fb9a83273d8a
- https://git.kernel.org/stable/c/1c4099dc0d6a01e76e4f7dd98e4b3e0d55d80ad9
