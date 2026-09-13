# [H] Bluetooth: MGMT: revalidate LOAD_CONN_PARAM queued update

## Summary
Severity: High
Advisory: CVE-2026-68394
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68394
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: revalidate LOAD_CONN_PARAM queued update

MGMT_OP_LOAD_CONN_PARAM queues conn_update_sync() when a single parameter
update changes an existing LE central connection. The queued work currently
stores a borrowed hci_conn_params entry from hdev->le_conn_params. A later
LOAD_CONN_PARAM request can clear disabled parameters and free that entry
before hci_cmd_sync_work() runs the queued callback.

Do not keep the borrowed hci_conn_params pointer in queued work. Queue the
hci_conn instead and hold a reference until the queued callback completes.
When the work runs, revalidate that the connection is still present, look
up the current hci_conn_params entry, and cancel the update if userspace
removed that entry while the work was pending.

Copy the interval values from the current params entry under hdev->lock,
then drop the lock and keep using hci_le_conn_update_sync() to issue the
update.

Validation reproduced this kernel report:
BUG: KASAN: slab-use-after-free in conn_update_sync+0x2a/0xf0 [bluetooth]
Read of size 1 at addr ffff88810c697126 by task kworker/u17:0/377
Workqueue: hci0 hci_cmd_sync_work [bluetooth]

Call Trace:
 <TASK>
 dump_stack_lvl+0x66/0xa0
 print_report+0xce/0x5f0
 kasan_report+0xe0/0x110
 conn_update_sync+0x2a/0xf0 [bluetooth]
 hci_cmd_sync_work+0x187/0x210 [bluetooth]
 process_one_work+0x4fd/0xbc0
 worker_thread+0x2d8/0x570
 kthread+0x1ad/0x1f0
 ret_from_fork+0x3c9/0x540
 ret_from_fork_asm+0x1a/0x30

Allocated by task 466:
 hci_conn_params_add+0xa6/0x240 [bluetooth]
 load_conn_param+0x4e1/0x850 [bluetooth]
 hci_sock_sendmsg+0x96b/0xf80 [bluetooth]

Freed by task 474:
 kfree+0x313/0x590
 hci_conn_params_clear_disabled+0x9b/0xc0 [bluetooth]
 load_conn_param+0x4bf/0x850 [bluetooth]
 hci_sock_sendmsg+0x96b/0xf80 [bluetooth]

## References
- https://git.kernel.org/stable/c/2bf282f8f715f5d05d6f4c49ffb3bd241c5e667e
- https://git.kernel.org/stable/c/57059ff14d81df4a970b2ea8d8f54431bb91a025
- https://git.kernel.org/stable/c/65ce6fe1b92112ba9064ded932c03180da3dd230
- https://git.kernel.org/stable/c/b82802b5ab26a7c69fc2e7a0f2baa3c13a6c21aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68394.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
