# [H] ext4: detect invalid INLINE_DATA + EXTENTS flag combination

## Summary
Severity: High
Advisory: CVE-2025-40167
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40167
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: detect invalid INLINE_DATA + EXTENTS flag combination

syzbot reported a BUG_ON in ext4_es_cache_extent() when opening a verity
file on a corrupted ext4 filesystem mounted without a journal.

The issue is that the filesystem has an inode with both the INLINE_DATA
and EXTENTS flags set:

    EXT4-fs error (device loop0): ext4_cache_extents:545: inode #15:
    comm syz.0.17: corrupted extent tree: lblk 0 < prev 66

Investigation revealed that the inode has both flags set:
    DEBUG: inode 15 - flag=1, i_inline_off=164, has_inline=1, extents_flag=1

This is an invalid combination since an inode should have either:
- INLINE_DATA: data stored directly in the inode
- EXTENTS: data stored in extent-mapped blocks

Having both flags causes ext4_has_inline_data() to return true, skipping
extent tree validation in __ext4_iget(). The unvalidated out-of-order
extents then trigger a BUG_ON in ext4_es_cache_extent() due to integer
underflow when calculating hole sizes.

Fix this by detecting this invalid flag combination early in ext4_iget()
and rejecting the corrupted inode.

## References
- https://git.kernel.org/stable/c/1437c95ab2a28b138d4521653583729f61ccb48b
- https://git.kernel.org/stable/c/1d3ad183943b38eec2acf72a0ae98e635dc8456b
- https://git.kernel.org/stable/c/1f5ccd22ff482639133f2a0fe08f6d19d0e68717
- https://git.kernel.org/stable/c/2e9e10657b04152ed0d6ecae8d0c02a3405e28f5
- https://git.kernel.org/stable/c/4954d297c91d292630ab43ba4d195dc371ce65d3
- https://git.kernel.org/stable/c/cb6039b68efa547b676a8a10fc4618d9d1865c23
- https://git.kernel.org/stable/c/de985264eef64be8a90595908f2e6a87946dad34
- https://git.kernel.org/stable/c/f061f7c331fc16250fc82aa68964f35821687217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40167.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
