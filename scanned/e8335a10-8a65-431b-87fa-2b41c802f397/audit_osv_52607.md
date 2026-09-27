# [M] CVE-2021-47637

## Summary
Severity: Medium
Advisory: CVE-2021-47637
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47637
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix deadlock in concurrent rename whiteout and inode writeback

Following hung tasks:
[   77.028764] task:kworker/u8:4    state:D stack:    0 pid:  132
[   77.028820] Call Trace:
[   77.029027]  schedule+0x8c/0x1b0
[   77.029067]  mutex_lock+0x50/0x60
[   77.029074]  ubifs_write_inode+0x68/0x1f0 [ubifs]
[   77.029117]  __writeback_single_inode+0x43c/0x570
[   77.029128]  writeback_sb_inodes+0x259/0x740
[   77.029148]  wb_writeback+0x107/0x4d0
[   77.029163]  wb_workfn+0x162/0x7b0

[   92.390442] task:aa              state:D stack:    0 pid: 1506
[   92.390448] Call Trace:
[   92.390458]  schedule+0x8c/0x1b0
[   92.390461]  wb_wait_for_completion+0x82/0xd0
[   92.390469]  __writeback_inodes_sb_nr+0xb2/0x110
[   92.390472]  writeback_inodes_sb_nr+0x14/0x20
[   92.390476]  ubifs_budget_space+0x705/0xdd0 [ubifs]
[   92.390503]  do_rename.cold+0x7f/0x187 [ubifs]
[   92.390549]  ubifs_rename+0x8b/0x180 [ubifs]
[   92.390571]  vfs_rename+0xdb2/0x1170
[   92.390580]  do_renameat2+0x554/0x770

, are caused by concurrent rename whiteout and inode writeback processes:
	rename_whiteout(Thread 1)	        wb_workfn(Thread2)
ubifs_rename
  do_rename
    lock_4_inodes (Hold ui_mutex)
    ubifs_budget_space
      make_free_space
        shrink_liability
	  __writeback_inodes_sb_nr
	    bdi_split_work_to_wbs (Queue new wb work)
					      wb_do_writeback(wb work)
						__writeback_single_inode
					          ubifs_write_inode
					            LOCK(ui_mutex)
							   ↑
	      wb_wait_for_completion (Wait wb work) <-- deadlock!

Reproducer (Detail program in [Link]):
  1. SYS_renameat2("/mp/dir/file", "/mp/dir/whiteout", RENAME_WHITEOUT)
  2. Consume out of space before kernel(mdelay) doing budget for whiteout

Fix it by doing whiteout space budget before locking ubifs inodes.
BTW, it also fixes wrong goto tag 'out_release' in whiteout budget
error handling path(It should at least recover dir i_size and unlock
4 ubifs inodes).

## References
- https://git.kernel.org/stable/c/37bdf1ad592555ecda1d55b89f6e393e4c0589d1
- https://git.kernel.org/stable/c/70e9090acc32348cedc5def0cd6d5c126efc97b9
- https://git.kernel.org/stable/c/83e42a78428fc354f5e2049935b84c8d8d29b787
- https://git.kernel.org/stable/c/8b278c8dcfb565cb65eceb62a38cbf7a7c326db5
- https://git.kernel.org/stable/c/9dddc8211430fb851ddf0b168e3a00c6f66cc185
- https://git.kernel.org/stable/c/afd427048047e8efdedab30e8888044e2be5aa9c
- https://git.kernel.org/stable/c/c58af8564a7b08757173009030b74baf4b2b762b
