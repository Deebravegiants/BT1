# [M] CVE-2021-47181

## Summary
Severity: Medium
Advisory: CVE-2021-47181
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47181
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: musb: tusb6010: check return value after calling platform_get_resource()

It will cause null-ptr-deref if platform_get_resource() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/1ba7605856e05fa991d4654ac69e5ace66c767b9
- https://git.kernel.org/stable/c/28be095eb612a489705d38c210afaf1103c5f4f8
- https://git.kernel.org/stable/c/3ee15f1af17407be381bcf06a78fa60b471242dd
- https://git.kernel.org/stable/c/679eee466d0f9ffa60a2b0c6ec19be5128927f04
- https://git.kernel.org/stable/c/b3f43659eb0b9af2e6ef18a8d829374610b19e7a
- https://git.kernel.org/stable/c/f87a79c04a33ab4e5be598c7b0867e6ef193d702
- https://git.kernel.org/stable/c/06cfb4cb2241e704d72e3045cf4d7dfb567fbce0
- https://git.kernel.org/stable/c/14651496a3de6807a17c310f63c894ea0c5d858e
