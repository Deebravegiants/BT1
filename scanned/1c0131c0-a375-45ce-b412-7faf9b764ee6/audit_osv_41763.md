# [H] f2fs: validate orphan inode entry count

## Summary
Severity: High
Advisory: CVE-2026-63818
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63818
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: validate orphan inode entry count

f2fs_recover_orphan_inodes() trusts the orphan block entry_count when
replaying orphan inodes from the checkpoint pack. A corrupted entry_count
larger than F2FS_ORPHANS_PER_BLOCK makes the recovery loop read past the
ino[] array and interpret footer or following data as inode numbers.

On a crafted image, mounting an unpatched kernel can drive orphan recovery
into f2fs_bug_on() and panic the kernel. Validate entry_count before
consuming entries so corrupted checkpoint data fails the mount with
-EFSCORRUPTED and requests fsck instead.

Set ERROR_INCONSISTENT_ORPHAN as well, so the corruption reason can be
recorded in the superblock s_errors[] field. This gives fsck a persistent
hint even though mount-time orphan recovery failure may leave no chance to
persist SBI_NEED_FSCK through a checkpoint.

## References
- https://git.kernel.org/stable/c/210c210c92d78fdf5051bc55c5c69044b1a2150a
- https://git.kernel.org/stable/c/2e12381d4495dc8b0ff042c6856022b2e359835c
- https://git.kernel.org/stable/c/550511a2470f6d204fa07b331f048bd2d3c51280
- https://git.kernel.org/stable/c/846c499a65816d13f1186e3090e825e8bb8bcb8b
- https://git.kernel.org/stable/c/8aad54746c251f2c2370118df766c0c82e2d2091
- https://git.kernel.org/stable/c/ad101d15716f5a24d1fa82a849f80430c805a3dd
- https://git.kernel.org/stable/c/d18c81f5d0ecd5796aa47d66d98f2dd54d8d0f70
- https://git.kernel.org/stable/c/d2f236196d542ccd8505736e41c3a1d3f0305f6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63818.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63818
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
