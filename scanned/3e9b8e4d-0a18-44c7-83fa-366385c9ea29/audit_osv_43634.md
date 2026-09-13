# [H] Bluetooth: hci_sync: Fix advertising data UAFs

## Summary
Severity: High
Advisory: CVE-2026-74509
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74509
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.184, >=6.2.0 <6.6.154, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: Fix advertising data UAFs

hci_find_adv_instance() returns an adv_info pointer that is valid only
while hdev->lock is held.  The advertising command-sync paths perform
instance lookups without that lock and, in some cases, retain the pointer
while waiting for a controller response.

An advertising termination event can therefore interleave as follows:

  hci_cmd_sync_work                 hci_rx_work
  hci_find_adv_instance()
  __hci_cmd_sync_status()
    wait for controller reply       hci_dev_lock()
                                    hci_remove_adv_instance()
                                      kfree(adv)
  adv->scan_rsp_changed = false

KASAN reported:

  BUG: KASAN: slab-use-after-free in hci_set_ext_scan_rsp_data_sync+0x2e1/0x300
  Write of size 1 at addr ffff88810a45d21d by task kworker/u17:0/88
  Workqueue: hci0 hci_cmd_sync_work
  Call Trace:
   hci_set_ext_scan_rsp_data_sync+0x2e1/0x300
   hci_schedule_adv_instance_sync+0x390/0x4c0
   hci_cmd_sync_work+0x173/0x300
  Allocated by task 87:
   hci_add_adv_instance+0x538/0xac0
   add_advertising+0x885/0x1160
  Freed by task 89:
   kfree+0x131/0x3c0
   hci_remove_adv_instance+0x1d8/0x3b0
   hci_le_ext_adv_term_evt+0x17b/0x730

Protect the instance lookup and payload construction in the extended
advertising, scan response, and periodic advertising data paths.  Snapshot
the advertising parameters under hdev->lock, but release the lock before
waiting for the controller.

Clear advertising-data dirty bits before issuing their commands and
restore them after a failure using a fresh lookup.  Likewise, update the
reported transmit power through a fresh lookup after the parameter command
completes.  No adv_info pointer then survives an HCI command wait.

## References
- https://git.kernel.org/stable/c/565971488191bf54a87a417abafab6ad0de72201
- https://git.kernel.org/stable/c/95cdcd8c82a501931fd3ae9b3811b0b6da167e94
- https://git.kernel.org/stable/c/b16ebdbebd2d37f4cdc590bc3e9db71fe90350a3
- https://git.kernel.org/stable/c/c4cec575a6d6f7c36808a3a0017b0675968bb06b
- https://git.kernel.org/stable/c/cdc36db204ffd97b947d64374cf23a210dc74777
- https://git.kernel.org/stable/c/eb1d8318764de7216e6dbba29a24d69f7ce51348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74509.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74509
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
