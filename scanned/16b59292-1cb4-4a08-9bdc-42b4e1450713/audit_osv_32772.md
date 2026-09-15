# [H] Bluetooth: btusb: avoid NULL pointer dereference in skb_dequeue()

## Summary
Severity: High
Advisory: CVE-2025-37918
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37918
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: avoid NULL pointer dereference in skb_dequeue()

A NULL pointer dereference can occur in skb_dequeue() when processing a
QCA firmware crash dump on WCN7851 (0489:e0f3).

[ 93.672166] Bluetooth: hci0: ACL memdump size(589824)

[ 93.672475] BUG: kernel NULL pointer dereference, address: 0000000000000008
[ 93.672517] Workqueue: hci0 hci_devcd_rx [bluetooth]
[ 93.672598] RIP: 0010:skb_dequeue+0x50/0x80

The issue stems from handle_dump_pkt_qca() returning 0 even when a dump
packet is successfully processed. This is because it incorrectly
forwards the return value of hci_devcd_init() (which returns 0 on
success). As a result, the caller (btusb_recv_acl_qca() or
btusb_recv_evt_qca()) assumes the packet was not handled and passes it
to hci_recv_frame(), leading to premature kfree() of the skb.

Later, hci_devcd_rx() attempts to dequeue the same skb from the dump
queue, resulting in a NULL pointer dereference.

Fix this by:
1. Making handle_dump_pkt_qca() return 0 on success and negative errno
   on failure, consistent with kernel conventions.
2. Splitting dump packet detection into separate functions for ACL
   and event packets for better structure and readability.

This ensures dump packets are properly identified and consumed, avoiding
double handling and preventing NULL pointer access.

## References
- https://git.kernel.org/stable/c/0317b033abcd1d8dd2798f0e2de5e84543d0bd22
- https://git.kernel.org/stable/c/2e8d44ebaa7babdd5c5ab50ca275826e241920d6
- https://git.kernel.org/stable/c/8563d9fabd8a4b726ba7acab4737c438bf11a059
- https://git.kernel.org/stable/c/b70b41591ec48c78ec6a885e1f57bfc4029e5e13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37918.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
