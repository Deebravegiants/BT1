# [H] fs: writeback: fix use-after-free in __mark_inode_dirty()

## Summary
Severity: High
Advisory: CVE-2025-39866
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39866
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.247, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: writeback: fix use-after-free in __mark_inode_dirty()

An use-after-free issue occurred when __mark_inode_dirty() get the
bdi_writeback that was in the progress of switching.

CPU: 1 PID: 562 Comm: systemd-random- Not tainted 6.6.56-gb4403bd46a8e #1
......
pstate: 60400005 (nZCv daif +PAN -UAO -TCO -DIT -SSBS BTYPE=--)
pc : __mark_inode_dirty+0x124/0x418
lr : __mark_inode_dirty+0x118/0x418
sp : ffffffc08c9dbbc0
........
Call trace:
 __mark_inode_dirty+0x124/0x418
 generic_update_time+0x4c/0x60
 file_modified+0xcc/0xd0
 ext4_buffered_write_iter+0x58/0x124
 ext4_file_write_iter+0x54/0x704
 vfs_write+0x1c0/0x308
 ksys_write+0x74/0x10c
 __arm64_sys_write+0x1c/0x28
 invoke_syscall+0x48/0x114
 el0_svc_common.constprop.0+0xc0/0xe0
 do_el0_svc+0x1c/0x28
 el0_svc+0x40/0xe4
 el0t_64_sync_handler+0x120/0x12c
 el0t_64_sync+0x194/0x198

Root cause is:

systemd-random-seed                         kworker
----------------------------------------------------------------------
___mark_inode_dirty                     inode_switch_wbs_work_fn

  spin_lock(&inode->i_lock);
  inode_attach_wb
  locked_inode_to_wb_and_lock_list
     get inode->i_wb
     spin_unlock(&inode->i_lock);
     spin_lock(&wb->list_lock)
  spin_lock(&inode->i_lock)
  inode_io_list_move_locked
  spin_unlock(&wb->list_lock)
  spin_unlock(&inode->i_lock)
                                    spin_lock(&old_wb->list_lock)
                                      inode_do_switch_wbs
                                        spin_lock(&inode->i_lock)
                                        inode->i_wb = new_wb
                                        spin_unlock(&inode->i_lock)
                                    spin_unlock(&old_wb->list_lock)
                                    wb_put_many(old_wb, nr_switched)
                                      cgwb_release
                                      old wb released
  wb_wakeup_delayed() accesses wb,
  then trigger the use-after-free
  issue

Fix this race condition by holding inode spinlock until
wb_wakeup_delayed() finished.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1edc2feb9c759a9883dfe81cb5ed231412d8b2e4
- https://git.kernel.org/stable/c/b187c976111960e6e54a6b1fff724f6e3d39406c
- https://git.kernel.org/stable/c/bf89b1f87c72df79cf76203f71fbf8349cd5c9de
- https://git.kernel.org/stable/c/c8c14adf80bd1a6e4a1d7ee9c2a816881c26d17a
- https://git.kernel.org/stable/c/d02d2c98d25793902f65803ab853b592c7a96b29
- https://git.kernel.org/stable/c/e2a14bbae5d8bacaa301362744a110e2be40a3a3
- https://git.kernel.org/stable/c/e63052921f1b25a836feb1500b841bff7a4a0456
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39866.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
