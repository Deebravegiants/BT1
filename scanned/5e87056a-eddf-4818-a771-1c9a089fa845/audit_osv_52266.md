# [M] CVE-2021-47260

## Summary
Severity: Medium
Advisory: CVE-2021-47260
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47260
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix a potential NULL dereference in nfs_get_client()

None of the callers are expecting NULL returns from nfs_get_client() so
this code will lead to an Oops.  It's better to return an error
pointer.  I expect that this is dead code so hopefully no one is
affected.

## References
- https://git.kernel.org/stable/c/0057ecef9f324007c0ba5fcca4ddd131178ce78b
- https://git.kernel.org/stable/c/09226e8303beeec10f2ff844d2e46d1371dc58e0
- https://git.kernel.org/stable/c/279ad78a00f8b9c5ff24171a59297187a3bd44b7
- https://git.kernel.org/stable/c/4b380a7d84ef2ce3f4f5bec5d8706ed937ac6502
- https://git.kernel.org/stable/c/58ddf61f10b8f9b7b1341644bfee2f1c6508d4e1
- https://git.kernel.org/stable/c/634f17ff1d59905eb3b4bbbc00805961d08beaee
- https://git.kernel.org/stable/c/a979e601000982a3ca693171a6d4dffc47f8ad00
- https://git.kernel.org/stable/c/fab8bfdfb4aac9e4e8363666333adfdf21e89106
