# [H] Bluetooth: hci_core: lookup hci_conn on RX path on protocol side

## Summary
Severity: High
Advisory: CVE-2025-68304
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68304
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_core: lookup hci_conn on RX path on protocol side

The hdev lock/lookup/unlock/use pattern in the packet RX path doesn't
ensure hci_conn* is not concurrently modified/deleted. This locking
appears to be leftover from before conn_hash started using RCU
commit bf4c63252490b ("Bluetooth: convert conn hash to RCU")
and not clear if it had purpose since then.

Currently, there are code paths that delete hci_conn* from elsewhere
than the ordered hdev->workqueue where the RX work runs in. E.g.
commit 5af1f84ed13a ("Bluetooth: hci_sync: Fix UAF on hci_abort_conn_sync")
introduced some of these, and there probably were a few others before
it.  It's better to do the locking so that even if these run
concurrently no UAF is possible.

Move the lookup of hci_conn and associated socket-specific conn to
protocol recv handlers, and do them within a single critical section
to cover hci_conn* usage and lookup.

syzkaller has reported a crash that appears to be this issue:

    [Task hdev->workqueue]          [Task 2]
                                    hci_disconnect_all_sync
    l2cap_recv_acldata(hcon)
                                      hci_conn_get(hcon)
                                      hci_abort_conn_sync(hcon)
                                        hci_dev_lock
      hci_dev_lock
                                        hci_conn_del(hcon)
      v-------------------------------- hci_dev_unlock
                                      hci_conn_put(hcon)
      conn = hcon->l2cap_data (UAF)

## References
- https://git.kernel.org/stable/c/79a2d4678ba90bdba577dc3af88cc900d6dcd5ee
- https://git.kernel.org/stable/c/ec74cdf77310c43b01b83ee898a9bd4b4b0b8e93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68304.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
