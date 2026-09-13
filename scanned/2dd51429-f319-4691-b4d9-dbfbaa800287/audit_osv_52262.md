# [M] CVE-2021-47256

## Summary
Severity: Medium
Advisory: CVE-2021-47256
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47256
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/memory-failure: make sure wait for page writeback in memory_failure

Our syzkaller trigger the "BUG_ON(!list_empty(&inode->i_wb_list))" in
clear_inode:

  kernel BUG at fs/inode.c:519!
  Internal error: Oops - BUG: 0 [#1] SMP
  Modules linked in:
  Process syz-executor.0 (pid: 249, stack limit = 0x00000000a12409d7)
  CPU: 1 PID: 249 Comm: syz-executor.0 Not tainted 4.19.95
  Hardware name: linux,dummy-virt (DT)
  pstate: 80000005 (Nzcv daif -PAN -UAO)
  pc : clear_inode+0x280/0x2a8
  lr : clear_inode+0x280/0x2a8
  Call trace:
    clear_inode+0x280/0x2a8
    ext4_clear_inode+0x38/0xe8
    ext4_free_inode+0x130/0xc68
    ext4_evict_inode+0xb20/0xcb8
    evict+0x1a8/0x3c0
    iput+0x344/0x460
    do_unlinkat+0x260/0x410
    __arm64_sys_unlinkat+0x6c/0xc0
    el0_svc_common+0xdc/0x3b0
    el0_svc_handler+0xf8/0x160
    el0_svc+0x10/0x218
  Kernel panic - not syncing: Fatal exception

A crash dump of this problem show that someone called __munlock_pagevec
to clear page LRU without lock_page: do_mmap -> mmap_region -> do_munmap
-> munlock_vma_pages_range -> __munlock_pagevec.

As a result memory_failure will call identify_page_state without
wait_on_page_writeback.  And after truncate_error_page clear the mapping
of this page.  end_page_writeback won't call sb_clear_inode_writeback to
clear inode->i_wb_list.  That will trigger BUG_ON in clear_inode!

Fix it by checking PageWriteback too to help determine should we skip
wait_on_page_writeback.

## References
- https://git.kernel.org/stable/c/566345aaabac853aa866f53a219c4b02a6beb527
- https://git.kernel.org/stable/c/6d210d547adc2218ef8b5bcf23518c5f2f1fd872
- https://git.kernel.org/stable/c/9e379da727a7a031be9b877cde7b9c34a0fb8306
- https://git.kernel.org/stable/c/d05267fd27a5c4f54e06daefa3035995d765ca0c
- https://git.kernel.org/stable/c/e8675d291ac007e1c636870db880f837a9ea112a
- https://git.kernel.org/stable/c/28788dc5c70597395b6b451dae4549bbaa8e2c56
