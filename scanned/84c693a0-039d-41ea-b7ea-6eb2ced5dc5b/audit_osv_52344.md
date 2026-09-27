# [M] CVE-2021-47351

## Summary
Severity: Medium
Advisory: CVE-2021-47351
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47351
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix races between xattr_{set|get} and listxattr operations

UBIFS may occur some problems with concurrent xattr_{set|get} and
listxattr operations, such as assertion failure, memory corruption,
stale xattr value[1].

Fix it by importing a new rw-lock in @ubifs_inode to serilize write
operations on xattr, concurrent read operations are still effective,
just like ext4.

[1] https://lore.kernel.org/linux-mtd/20200630130438.141649-1-houtao1@huawei.com

## References
- https://git.kernel.org/stable/c/c0756f75c22149d20fcb7d8409827cee905eb386
- https://git.kernel.org/stable/c/f4e3634a3b642225a530c292fdb1e8a4007507f5
- https://git.kernel.org/stable/c/38dde03eb239605f428f3f1e4baa73d4933a4cc6
- https://git.kernel.org/stable/c/7adc05b73d91a5e3d4ca7714fa53ad9b70c53d08
- https://git.kernel.org/stable/c/9558612cb829f2c022b788f55d6b8437d5234a82
