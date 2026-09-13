# [H] ext4: fix double-free of blocks due to wrong extents moved_len

## Summary
Severity: High
Advisory: CVE-2024-26704
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26704
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix double-free of blocks due to wrong extents moved_len

In ext4_move_extents(), moved_len is only updated when all moves are
successfully executed, and only discards orig_inode and donor_inode
preallocations when moved_len is not zero. When the loop fails to exit
after successfully moving some extents, moved_len is not updated and
remains at 0, so it does not discard the preallocations.

If the moved extents overlap with the preallocated extents, the
overlapped extents are freed twice in ext4_mb_release_inode_pa() and
ext4_process_freed_data() (as described in commit 94d7c16cbbbd ("ext4:
Fix double-free of blocks with EXT4_IOC_MOVE_EXT")), and bb_free is
incremented twice. Hence when trim is executed, a zero-division bug is
triggered in mb_update_avg_fragment_size() because bb_free is not zero
and bb_fragments is zero.

Therefore, update move_len after each extent move to avoid the issue.

## References
- https://git.kernel.org/stable/c/185eab30486ba3e7bf8b9c2e049c79a06ffd2bc1
- https://git.kernel.org/stable/c/2883940b19c38d5884c8626483811acf4d7e148f
- https://git.kernel.org/stable/c/55583e899a5357308274601364741a83e78d6ac4
- https://git.kernel.org/stable/c/559ddacb90da1d8786dd8ec4fd76bbfa404eaef6
- https://git.kernel.org/stable/c/afba9d11320dad5ce222ac8964caf64b7b4bedb1
- https://git.kernel.org/stable/c/afbcad9ae7d6d11608399188f03a837451b6b3a1
- https://git.kernel.org/stable/c/b4fbb89d722cbb16beaaea234b7230faaaf68c71
- https://git.kernel.org/stable/c/d033a555d9a1cf53dbf3301af7199cc4a4c8f537
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26704.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26704
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
