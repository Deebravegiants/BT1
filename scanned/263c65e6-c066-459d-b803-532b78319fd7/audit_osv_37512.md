# [H] Bluetooth: hci_sync: fix stack buffer overflow in hci_le_big_create_sync

## Summary
Severity: High
Advisory: CVE-2026-31772
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31772
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.81, >=6.13.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: fix stack buffer overflow in hci_le_big_create_sync

hci_le_big_create_sync() uses DEFINE_FLEX to allocate a
struct hci_cp_le_big_create_sync on the stack with room for 0x11 (17)
BIS entries.  However, conn->num_bis can hold up to HCI_MAX_ISO_BIS (31)
entries — validated against ISO_MAX_NUM_BIS (0x1f) in the caller
hci_conn_big_create_sync().  When conn->num_bis is between 18 and 31,
the memcpy that copies conn->bis into cp->bis writes up to 14 bytes
past the stack buffer, corrupting adjacent stack memory.

This is trivially reproducible: binding an ISO socket with
bc_num_bis = ISO_MAX_NUM_BIS (31) and calling listen() will
eventually trigger hci_le_big_create_sync() from the HCI command
sync worker, causing a KASAN-detectable stack-out-of-bounds write:

  BUG: KASAN: stack-out-of-bounds in hci_le_big_create_sync+0x256/0x3b0
  Write of size 31 at addr ffffc90000487b48 by task kworker/u9:0/71

Fix this by changing the DEFINE_FLEX count from the incorrect 0x11 to
HCI_MAX_ISO_BIS, which matches the maximum number of BIS entries that
conn->bis can actually carry.

## References
- https://git.kernel.org/stable/c/aba0aea354015794e8312dd7efe726967e58aefe
- https://git.kernel.org/stable/c/bc39a094730ce062fa034a529c93147c096cb488
- https://git.kernel.org/stable/c/eaf32002ca7b1ba51c9f140991fd9febe6de79f0
- https://git.kernel.org/stable/c/f5d446624345d309e7a4a1b27ea9f028d6a8c5d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31772.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31772
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
