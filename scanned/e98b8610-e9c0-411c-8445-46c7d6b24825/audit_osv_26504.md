# [H] ext4: add bounds checking in get_max_inline_xattr_value_size()

## Summary
Severity: High
Advisory: CVE-2023-53285
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53285
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: add bounds checking in get_max_inline_xattr_value_size()

Normally the extended attributes in the inode body would have been
checked when the inode is first opened, but if someone is writing to
the block device while the file system is mounted, it's possible for
the inode table to get corrupted.  Add bounds checking to avoid
reading beyond the end of allocated memory if this happens.

## References
- https://git.kernel.org/stable/c/1d2caddbeeee56fbbc36b428c5b909c3ad88eb7f
- https://git.kernel.org/stable/c/2220eaf90992c11d888fe771055d4de330385f01
- https://git.kernel.org/stable/c/3d7b8fbcd2273e2b9f4c6de5ce2f4c0cd3cb1205
- https://git.kernel.org/stable/c/4597554b4f7b29e7fd78aa449bab648f8da4ee2c
- https://git.kernel.org/stable/c/486efbbc9445dca7890a1b86adbccb88b91284b0
- https://git.kernel.org/stable/c/5a229d21b98d132673096710e8281ef522dab1d1
- https://git.kernel.org/stable/c/88a06a94942c5c0a896e9da1113a6bb29e36cbef
- https://git.kernel.org/stable/c/e780058bd75614b66882bc02620ddbd884171560
- https://git.kernel.org/stable/c/f22b274429e88d3dc7e79d375b56ce4f2f59f0b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53285.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
