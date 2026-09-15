# [H] ocfs2: fix uninitialized value in ocfs2_file_read_iter()

## Summary
Severity: High
Advisory: CVE-2024-53155
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53155
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix uninitialized value in ocfs2_file_read_iter()

Syzbot has reported the following KMSAN splat:

BUG: KMSAN: uninit-value in ocfs2_file_read_iter+0x9a4/0xf80
 ocfs2_file_read_iter+0x9a4/0xf80
 __io_read+0x8d4/0x20f0
 io_read+0x3e/0xf0
 io_issue_sqe+0x42b/0x22c0
 io_wq_submit_work+0xaf9/0xdc0
 io_worker_handle_work+0xd13/0x2110
 io_wq_worker+0x447/0x1410
 ret_from_fork+0x6f/0x90
 ret_from_fork_asm+0x1a/0x30

Uninit was created at:
 __alloc_pages_noprof+0x9a7/0xe00
 alloc_pages_mpol_noprof+0x299/0x990
 alloc_pages_noprof+0x1bf/0x1e0
 allocate_slab+0x33a/0x1250
 ___slab_alloc+0x12ef/0x35e0
 kmem_cache_alloc_bulk_noprof+0x486/0x1330
 __io_alloc_req_refill+0x84/0x560
 io_submit_sqes+0x172f/0x2f30
 __se_sys_io_uring_enter+0x406/0x41c0
 __x64_sys_io_uring_enter+0x11f/0x1a0
 x64_sys_call+0x2b54/0x3ba0
 do_syscall_64+0xcd/0x1e0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Since an instance of 'struct kiocb' may be passed from the block layer
with 'private' field uninitialized, introduce 'ocfs2_iocb_init_rw_locked()'
and use it from where 'ocfs2_dio_end_io()' might take care, i.e. in
'ocfs2_file_read_iter()' and 'ocfs2_file_write_iter()'.

## References
- https://git.kernel.org/stable/c/366c933c2ab34dd6551acc03b4872726b7605143
- https://git.kernel.org/stable/c/66b7ddd1804e2c4216dd7ead8eeb746cdbb3b62f
- https://git.kernel.org/stable/c/6c8f8d1e595dabd5389817f6d798cc8bd95c40ab
- https://git.kernel.org/stable/c/83f8713a0ef1d55d6a287bcfadcaab8245ac5098
- https://git.kernel.org/stable/c/8c966150d5abff58c3c2bdb9a6e63fd773782905
- https://git.kernel.org/stable/c/8e0de82ed18ba0e71f817adbd81317fd1032ca5a
- https://git.kernel.org/stable/c/adc77b19f62d7e80f98400b2fca9d700d2afdd6f
- https://git.kernel.org/stable/c/dc78efe556fed162d48736ef24066f42e463e27c
- https://git.kernel.org/stable/c/f4078ef38d3163e6be47403a619558b19c4bfccd
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53155.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
