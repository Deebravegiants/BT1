# [M] nilfs2: fix deadlock in nilfs_count_free_blocks()

## Summary
Severity: Medium
Advisory: CVE-2022-49850
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49850
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix deadlock in nilfs_count_free_blocks()

A semaphore deadlock can occur if nilfs_get_block() detects metadata
corruption while locating data blocks and a superblock writeback occurs at
the same time:

task 1                               task 2
------                               ------
* A file operation *
nilfs_truncate()
  nilfs_get_block()
    down_read(rwsem A) <--
    nilfs_bmap_lookup_contig()
      ...                            generic_shutdown_super()
                                       nilfs_put_super()
                                         * Prepare to write superblock *
                                         down_write(rwsem B) <--
                                         nilfs_cleanup_super()
      * Detect b-tree corruption *         nilfs_set_log_cursor()
      nilfs_bmap_convert_error()             nilfs_count_free_blocks()
        __nilfs_error()                        down_read(rwsem A) <--
          nilfs_set_error()
            down_write(rwsem B) <--

                           *** DEADLOCK ***

Here, nilfs_get_block() readlocks rwsem A (= NILFS_MDT(dat_inode)->mi_sem)
and then calls nilfs_bmap_lookup_contig(), but if it fails due to metadata
corruption, __nilfs_error() is called from nilfs_bmap_convert_error()
inside the lock section.

Since __nilfs_error() calls nilfs_set_error() unless the filesystem is
read-only and nilfs_set_error() attempts to writelock rwsem B (=
nilfs->ns_sem) to write back superblock exclusively, hierarchical lock
acquisition occurs in the order rwsem A -> rwsem B.

Now, if another task starts updating the superblock, it may writelock
rwsem B during the lock sequence above, and can deadlock trying to
readlock rwsem A in nilfs_count_free_blocks().

However, there is actually no need to take rwsem A in
nilfs_count_free_blocks() because it, within the lock section, only reads
a single integer data on a shared struct with
nilfs_sufile_get_ncleansegs().  This has been the case after commit
aa474a220180 ("nilfs2: add local variable to cache the number of clean
segments"), that is, even before this bug was introduced.

So, this resolves the deadlock problem by just not taking the semaphore in
nilfs_count_free_blocks().

## References
- https://git.kernel.org/stable/c/1d4ff73062096c21b47954d2996b4df259777bda
- https://git.kernel.org/stable/c/36ff974b0310771417c0be64b64aa221bd70d63d
- https://git.kernel.org/stable/c/3c89ca6d3dfa6c09c515807a7a97a521f5d5147e
- https://git.kernel.org/stable/c/8ac932a4921a96ca52f61935dbba64ea87bbd5dc
- https://git.kernel.org/stable/c/8b4506cff6630bb474bb46a2a75c31e533a756ba
- https://git.kernel.org/stable/c/abc082aac0d9b6b926038fc3adb7008306581be2
- https://git.kernel.org/stable/c/cb029b54953420f7a2d65100f1c5107f14411bdc
- https://git.kernel.org/stable/c/f0cc93080d4c09510b74ecba87fd778cca390bb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49850.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49850
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
