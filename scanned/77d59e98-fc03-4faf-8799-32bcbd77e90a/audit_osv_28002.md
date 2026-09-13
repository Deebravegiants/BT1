# [M] nilfs2: fix failure to detect DAT corruption in btree and direct mappings

## Summary
Severity: Medium
Advisory: CVE-2024-26956
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26956
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix failure to detect DAT corruption in btree and direct mappings

Patch series "nilfs2: fix kernel bug at submit_bh_wbc()".

This resolves a kernel BUG reported by syzbot.  Since there are two
flaws involved, I've made each one a separate patch.

The first patch alone resolves the syzbot-reported bug, but I think
both fixes should be sent to stable, so I've tagged them as such.


This patch (of 2):

Syzbot has reported a kernel bug in submit_bh_wbc() when writing file data
to a nilfs2 file system whose metadata is corrupted.

There are two flaws involved in this issue.

The first flaw is that when nilfs_get_block() locates a data block using
btree or direct mapping, if the disk address translation routine
nilfs_dat_translate() fails with internal code -ENOENT due to DAT metadata
corruption, it can be passed back to nilfs_get_block().  This causes
nilfs_get_block() to misidentify an existing block as non-existent,
causing both data block lookup and insertion to fail inconsistently.

The second flaw is that nilfs_get_block() returns a successful status in
this inconsistent state.  This causes the caller __block_write_begin_int()
or others to request a read even though the buffer is not mapped,
resulting in a BUG_ON check for the BH_Mapped flag in submit_bh_wbc()
failing.

This fixes the first issue by changing the return value to code -EINVAL
when a conversion using DAT fails with code -ENOENT, avoiding the
conflicting condition that leads to the kernel bug described above.  Here,
code -EINVAL indicates that metadata corruption was detected during the
block lookup, which will be properly handled as a file system error and
converted to -EIO when passing through the nilfs2 bmap layer.

## References
- https://git.kernel.org/stable/c/2e2619ff5d0def4bb6c2037a32a6eaa28dd95c84
- https://git.kernel.org/stable/c/46b832e09d43b394ac0f6d9485d2b1a06593f0b7
- https://git.kernel.org/stable/c/82827ca21e7c8a91384c5baa656f78a5adfa4ab4
- https://git.kernel.org/stable/c/9cbe1ad5f4354f4df1445e5f4883983328cd6d8e
- https://git.kernel.org/stable/c/a8e4d098de1c0f4c5c1f2ed4633a860f0da6d713
- https://git.kernel.org/stable/c/b67189690eb4b7ecc84ae16fa1e880e0123eaa35
- https://git.kernel.org/stable/c/c3b5c5c31e723b568f83d8cafab8629d9d830ffb
- https://git.kernel.org/stable/c/f2f26b4a84a0ef41791bd2d70861c8eac748f4ba
- https://git.kernel.org/stable/c/f69e81396aea66304d214f175aa371f1b5578862
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26956.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
