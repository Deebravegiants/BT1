# [H] CVE-2021-47239

## Summary
Severity: High
Advisory: CVE-2021-47239
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47239
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: fix possible use-after-free in smsc75xx_bind

The commit 46a8b29c6306 ("net: usb: fix memory leak in smsc75xx_bind")
fails to clean up the work scheduled in smsc75xx_reset->
smsc75xx_set_multicast, which leads to use-after-free if the work is
scheduled to start after the deallocation. In addition, this patch
also removes a dangling pointer - dev->data[0].

This patch calls cancel_work_sync to cancel the scheduled work and set
the dangling pointer to NULL.

## References
- https://git.kernel.org/stable/c/c4e3be2e7742863e454ce31faf8fd0109c00050b
- https://git.kernel.org/stable/c/14616c372a7be01a2fb8c56c9d8debd232b9e43d
- https://git.kernel.org/stable/c/2fc8300c9cfa5167fcb5b1a2a07db6f53e82f59b
- https://git.kernel.org/stable/c/4252bf6c2b245f47011098113d405ffad6ad5d5b
- https://git.kernel.org/stable/c/56b786d86694e079d8aad9b314e015cd4ac02a3d
- https://git.kernel.org/stable/c/570a52cf3e01d19f7fd1a251dfc52b0cd86c13cb
- https://git.kernel.org/stable/c/64160d1741a3de5204d1a822e058e0b4cc526504
- https://git.kernel.org/stable/c/7cc8b2e05fcea6edd022d26e82091d781af8fd9b
