# [H] f2fs: compress: fix UAF of f2fs_inode_info in f2fs_free_dic

## Summary
Severity: High
Advisory: CVE-2025-38627
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38627
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.175, >=6.2.0 <6.6.118, >=6.7.0 <6.12.78, >=6.13.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix UAF of f2fs_inode_info in f2fs_free_dic

The decompress_io_ctx may be released asynchronously after
I/O completion. If this file is deleted immediately after read,
and the kworker of processing post_read_wq has not been executed yet
due to high workloads, It is possible that the inode(f2fs_inode_info)
is evicted and freed before it is used f2fs_free_dic.

    The UAF case as below:
    Thread A                                      Thread B
    - f2fs_decompress_end_io
     - f2fs_put_dic
      - queue_work
        add free_dic work to post_read_wq
                                                   - do_unlink
                                                    - iput
                                                     - evict
                                                      - call_rcu
    This file is deleted after read.

    Thread C                                 kworker to process post_read_wq
    - rcu_do_batch
     - f2fs_free_inode
      - kmem_cache_free
     inode is freed by rcu
                                             - process_scheduled_works
                                              - f2fs_late_free_dic
                                               - f2fs_free_dic
                                                - f2fs_release_decomp_mem
                                      read (dic->inode)->i_compress_algorithm

This patch store compress_algorithm and sbi in dic to avoid inode UAF.

In addition, the previous solution is deprecated in [1] may cause system hang.
[1] https://lore.kernel.org/all/c36ab955-c8db-4a8b-a9d0-f07b5f426c3f@kernel.org

## References
- https://git.kernel.org/stable/c/39868685c2a94a70762bc6d77dc81d781d05bff5
- https://git.kernel.org/stable/c/5d604d40cd3232b09cb339941ef958e49283ed0a
- https://git.kernel.org/stable/c/74cbeeca4f16823ba58c882e1d8b836c0e39c93d
- https://git.kernel.org/stable/c/8fae5b6addd5f6895e03797b56e3c7b9f9cd15c9
- https://git.kernel.org/stable/c/cc81768212cdc509e5a986274db7bc24d18cde19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38627.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
