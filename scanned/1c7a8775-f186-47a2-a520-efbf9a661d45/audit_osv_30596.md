# [H] Bluetooth: MGMT: Fix possible deadlocks

## Summary
Severity: High
Advisory: CVE-2024-53207
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53207
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: Fix possible deadlocks

This fixes possible deadlocks like the following caused by
hci_cmd_sync_dequeue causing the destroy function to run:

 INFO: task kworker/u19:0:143 blocked for more than 120 seconds.
       Tainted: G        W  O        6.8.0-2024-03-19-intel-next-iLS-24ww14 #1
 "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
 task:kworker/u19:0   state:D stack:0     pid:143   tgid:143   ppid:2      flags:0x00004000
 Workqueue: hci0 hci_cmd_sync_work [bluetooth]
 Call Trace:
  <TASK>
  __schedule+0x374/0xaf0
  schedule+0x3c/0xf0
  schedule_preempt_disabled+0x1c/0x30
  __mutex_lock.constprop.0+0x3ef/0x7a0
  __mutex_lock_slowpath+0x13/0x20
  mutex_lock+0x3c/0x50
  mgmt_set_connectable_complete+0xa4/0x150 [bluetooth]
  ? kfree+0x211/0x2a0
  hci_cmd_sync_dequeue+0xae/0x130 [bluetooth]
  ? __pfx_cmd_complete_rsp+0x10/0x10 [bluetooth]
  cmd_complete_rsp+0x26/0x80 [bluetooth]
  mgmt_pending_foreach+0x4d/0x70 [bluetooth]
  __mgmt_power_off+0x8d/0x180 [bluetooth]
  ? _raw_spin_unlock_irq+0x23/0x40
  hci_dev_close_sync+0x445/0x5b0 [bluetooth]
  hci_set_powered_sync+0x149/0x250 [bluetooth]
  set_powered_sync+0x24/0x60 [bluetooth]
  hci_cmd_sync_work+0x90/0x150 [bluetooth]
  process_one_work+0x13e/0x300
  worker_thread+0x2f7/0x420
  ? __pfx_worker_thread+0x10/0x10
  kthread+0x107/0x140
  ? __pfx_kthread+0x10/0x10
  ret_from_fork+0x3d/0x60
  ? __pfx_kthread+0x10/0x10
  ret_from_fork_asm+0x1b/0x30
  </TASK>

## References
- https://git.kernel.org/stable/c/5703fb1d85f653e35b327b14de4db7da239e4fd9
- https://git.kernel.org/stable/c/6a25ce9b4af6dc26ee2b9c32d6bd37620bf9739e
- https://git.kernel.org/stable/c/a66dfaf18fd61bb75ef8cee83db46b2aadf153d0
- https://git.kernel.org/stable/c/c3f594a3473d6429a0bcf2004cb2885368741b79
- https://git.kernel.org/stable/c/cac34e44281f1f1bd842adbbcfe3ef9ff0905111
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53207.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
