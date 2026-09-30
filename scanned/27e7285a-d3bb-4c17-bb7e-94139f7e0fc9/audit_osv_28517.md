# [H] f2fs: compress: fix to cover {reserve,release}_compress_blocks() w/ cp_rwsem lock

## Summary
Severity: High
Advisory: CVE-2024-34027
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-34027
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix to cover {reserve,release}_compress_blocks() w/ cp_rwsem lock

It needs to cover {reserve,release}_compress_blocks() w/ cp_rwsem lock
to avoid racing with checkpoint, otherwise, filesystem metadata including
blkaddr in dnode, inode fields and .total_valid_block_count may be
corrupted after SPO case.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0a4ed2d97cb6d044196cc3e726b6699222b41019
- https://git.kernel.org/stable/c/329edb7c9e3b6ca27e6ca67ab1cdda1740fb3a2b
- https://git.kernel.org/stable/c/5d47d63883735718825ca2efc4fca6915469774f
- https://git.kernel.org/stable/c/69136304fd144144a4828c7b7b149d0f80321ba4
- https://git.kernel.org/stable/c/a6e1f7744e9b84f86a629a76024bba8468aa153b
- https://git.kernel.org/stable/c/b5bac43875aa27ec032dbbb86173baae6dce6182
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34027.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
