# [H] Bluetooth: hci_conn: fix potential UAF in create_big_sync

## Summary
Severity: High
Advisory: CVE-2026-46111
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46111
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.183, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: fix potential UAF in create_big_sync

Add hci_conn_valid() check in create_big_sync() to detect stale
connections before proceeding with BIG creation. Handle the
resulting -ECANCELED in create_big_complete() and re-validate the
connection under hci_dev_lock() before dereferencing, matching the
pattern used by create_le_conn_complete() and create_pa_complete().

Keep the hci_conn object alive across the async boundary by taking
a reference via hci_conn_get() when queueing create_big_sync(), and
dropping it in the completion callback. The refcount and the lock
are complementary: the refcount keeps the object allocated, while
hci_dev_lock() serializes hci_conn_hash_del()'s list_del_rcu() on
hdev->conn_hash, as required by hci_conn_del().

hci_conn_put() is called outside hci_dev_unlock() so the final put
(which resolves to kfree() via bt_link_release) does not run under
hdev->lock, though the release path would be safe either way.

Without this, create_big_complete() would unconditionally
dereference the conn pointer on error, causing a use-after-free
via hci_connect_cfm() and hci_conn_del().

## References
- https://git.kernel.org/stable/c/0beddb0c380bed5f5b8e61ddbe14635bb73d0b41
- https://git.kernel.org/stable/c/1750a2df0eab61dc421a7afae74abdd239a44b85
- https://git.kernel.org/stable/c/6823f730bf195fc296d9edd09e2ca94bc1ff5584
- https://git.kernel.org/stable/c/d41093723e47255d7d74df86e2736711c1b8486e
- https://git.kernel.org/stable/c/dc34f8d8240f25dd137dc2758ebbcc75e3779142
- https://git.kernel.org/stable/c/f8eaf92c57ad99358dd372580d5ff87623343a72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
