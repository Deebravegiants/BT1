# [H] btrfs: avoid potential out-of-bounds in btrfs_encode_fh()

## Summary
Severity: High
Advisory: CVE-2025-40205
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40205
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: avoid potential out-of-bounds in btrfs_encode_fh()

The function btrfs_encode_fh() does not properly account for the three
cases it handles.

Before writing to the file handle (fh), the function only returns to the
user BTRFS_FID_SIZE_NON_CONNECTABLE (5 dwords, 20 bytes) or
BTRFS_FID_SIZE_CONNECTABLE (8 dwords, 32 bytes).

However, when a parent exists and the root ID of the parent and the
inode are different, the function writes BTRFS_FID_SIZE_CONNECTABLE_ROOT
(10 dwords, 40 bytes).

If *max_len is not large enough, this write goes out of bounds because
BTRFS_FID_SIZE_CONNECTABLE_ROOT is greater than
BTRFS_FID_SIZE_CONNECTABLE originally returned.

This results in an 8-byte out-of-bounds write at
fid->parent_root_objectid = parent_root_id.

A previous attempt to fix this issue was made but was lost.

https://lore.kernel.org/all/4CADAEEC020000780001B32C@vpn.id2.novell.com/

Although this issue does not seem to be easily triggerable, it is a
potential memory corruption bug that should be fixed. This patch
resolves the issue by ensuring the function returns the appropriate size
for all three cases and validates that *max_len is large enough before
writing any data.

## References
- https://git.kernel.org/stable/c/0276c8582488022f057b4cec21975a5edf079f47
- https://git.kernel.org/stable/c/361d67276eb8ec6be8f27f4ad6c6090459438fee
- https://git.kernel.org/stable/c/43143776b0a7604d873d1a6f3e552a00aa930224
- https://git.kernel.org/stable/c/60de2f55d2aca53e81b4ef2a67d7cc9e1eb677db
- https://git.kernel.org/stable/c/742b44342204e5dfe3926433823623c1a0c581df
- https://git.kernel.org/stable/c/d3a9a8e1275eb9b87f006b5562a287aea3f6885f
- https://git.kernel.org/stable/c/d91f6626133698362bba08fbc04bd72c466806d3
- https://git.kernel.org/stable/c/dff4f9ff5d7f289e4545cc936362e01ed3252742
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40205.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40205
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
