# [H] nilfs2: fix state management in error path of log writing function

## Summary
Severity: High
Advisory: CVE-2024-47669
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47669
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix state management in error path of log writing function

After commit a694291a6211 ("nilfs2: separate wait function from
nilfs_segctor_write") was applied, the log writing function
nilfs_segctor_do_construct() was able to issue I/O requests continuously
even if user data blocks were split into multiple logs across segments,
but two potential flaws were introduced in its error handling.

First, if nilfs_segctor_begin_construction() fails while creating the
second or subsequent logs, the log writing function returns without
calling nilfs_segctor_abort_construction(), so the writeback flag set on
pages/folios will remain uncleared.  This causes page cache operations to
hang waiting for the writeback flag.  For example,
truncate_inode_pages_final(), which is called via nilfs_evict_inode() when
an inode is evicted from memory, will hang.

Second, the NILFS_I_COLLECTED flag set on normal inodes remain uncleared. 
As a result, if the next log write involves checkpoint creation, that's
fine, but if a partial log write is performed that does not, inodes with
NILFS_I_COLLECTED set are erroneously removed from the "sc_dirty_files"
list, and their data and b-tree blocks may not be written to the device,
corrupting the block mapping.

Fix these issues by uniformly calling nilfs_segctor_abort_construction()
on failure of each step in the loop in nilfs_segctor_do_construct(),
having it clean up logs and segment usages according to progress, and
correcting the conditions for calling nilfs_redirty_inodes() to ensure
that the NILFS_I_COLLECTED flag is cleared.

## References
- https://git.kernel.org/stable/c/036441e8438b29111fa75008f0ce305fb4e83c0a
- https://git.kernel.org/stable/c/0a1a961bde4351dc047ffdeb2f1311ca16a700cc
- https://git.kernel.org/stable/c/30562eff4a6dd35c4b5be9699ef61ad9f5f20a06
- https://git.kernel.org/stable/c/3e349d7191f0688fc9808ef24fd4e4b4ef5ca876
- https://git.kernel.org/stable/c/40a2757de2c376ef8a08d9ee9c81e77f3c750adf
- https://git.kernel.org/stable/c/6576dd6695f2afca3f4954029ac4a64f82ba60ab
- https://git.kernel.org/stable/c/74866c16ea2183f52925fa5d76061a1fe7f7737b
- https://git.kernel.org/stable/c/efdde00d4a1ef10bb71e09ebc67823a3d3ad725b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47669.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
