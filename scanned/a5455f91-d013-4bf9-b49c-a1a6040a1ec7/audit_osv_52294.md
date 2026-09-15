# [H] CVE-2021-47295

## Summary
Severity: High
Advisory: CVE-2021-47295
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47295
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: fix memory leak in tcindex_partial_destroy_work

Syzbot reported memory leak in tcindex_set_parms(). The problem was in
non-freed perfect hash in tcindex_partial_destroy_work().

In tcindex_set_parms() new tcindex_data is allocated and some fields from
old one are copied to new one, but not the perfect hash. Since
tcindex_partial_destroy_work() is the destroy function for old
tcindex_data, we need to free perfect hash to avoid memory leak.

## References
- https://git.kernel.org/stable/c/18c3fa7a7fdbb4d21dafc8a7710ae2c1680930f6
- https://git.kernel.org/stable/c/01d0d2b8b4e3cf2110baba9371c0c3d04ad5c77b
- https://git.kernel.org/stable/c/372ae77cf11d11fb118cbe2d37def9dd5f826abd
- https://git.kernel.org/stable/c/3abebc503a5148072052c229c6b04b329a420ecd
- https://git.kernel.org/stable/c/53af9c793f644d5841d84d8e0ad83bd7ab47f3e0
- https://git.kernel.org/stable/c/7a6fb69bbcb21e9ce13bdf18c008c268874f0480
- https://git.kernel.org/stable/c/7c183dc0af472dec33d2c0786a5e356baa8cad19
- https://git.kernel.org/stable/c/8d7924ce85bae64e7a67c366c7c50840f49f3a62
- https://git.kernel.org/stable/c/8e9662fde6d63c78eb1350f6167f64c9d71a865b
- https://git.kernel.org/stable/c/cac71d27745f92ee13f0ecc668ffe151a4a9c9b1
- https://git.kernel.org/stable/c/f5051bcece50140abd1a11a2d36dc3ec5484fc32
