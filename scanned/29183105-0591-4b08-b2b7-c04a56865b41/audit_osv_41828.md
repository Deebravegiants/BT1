# [H] Bluetooth: hci_sync: fix UAF in hci_le_create_cis_sync

## Summary
Severity: High
Advisory: CVE-2026-63944
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63944
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: fix UAF in hci_le_create_cis_sync

hci_le_create_cis_sync() dereferences conn->conn_timeout after releasing
both rcu_read_lock() and hci_dev_lock(hdev).  The conn pointer was
obtained from an RCU-protected iteration over hdev->conn_hash.list and
is not valid once these locks are dropped.  A concurrent disconnect can
free the hci_conn between the unlock and the dereference, causing a
use-after-free read.

The cancellation mechanism in hci_conn_del() cannot prevent this because
hci_le_create_cis_pending() queues hci_create_cis_sync with data=NULL:

    hci_cmd_sync_queue(hdev, hci_create_cis_sync, NULL, NULL);

While hci_conn_del() dequeues with data=conn:

    hci_cmd_sync_dequeue(hdev, NULL, conn, NULL);

Since NULL != conn, the lookup in _hci_cmd_sync_lookup_entry() never
matches, and the pending work item is not cancelled.

Fix this by saving conn->conn_timeout into a local variable while the
locks are still held, so the stale conn pointer is never dereferenced
after unlock.

This is the same class of bug as the one fixed by commit 035c25007c9e
("Bluetooth: hci_sync: Fix UAF on le_read_features_complete") which
addressed the identical pattern in a different function.

This vulnerability was identified using 0sec.ai, an open-source
automated security auditing platform (https://github.com/0sec-labs).

## References
- https://git.kernel.org/stable/c/380e67b1794a9a281a0cb592b4e62077fbd0c8ca
- https://git.kernel.org/stable/c/a55618c0f4cead9e59c63f5ee030d393fd70d861
- https://git.kernel.org/stable/c/a921957d39290143629eb38c4f74b9bef8035d0a
- https://git.kernel.org/stable/c/bfea6091e0fffb270c20e74384b660910277eb6c
- https://git.kernel.org/stable/c/d9019210c8c30d40eb20094274cc647e352f48f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63944.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63944
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
