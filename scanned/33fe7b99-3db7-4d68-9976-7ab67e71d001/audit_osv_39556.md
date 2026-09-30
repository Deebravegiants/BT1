# [H] Bluetooth: hci_event: Fix OOB read and infinite loop in hci_le_create_big_complete_evt

## Summary
Severity: High
Advisory: CVE-2026-46138
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46138
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: Fix OOB read and infinite loop in hci_le_create_big_complete_evt

hci_le_create_big_complete_evt() iterates over BT_BOUND connections for
a BIG handle using a while loop, accessing ev->bis_handle[i++] on each
iteration.  However, there is no check that i stays within ev->num_bis
before the array access.

When a controller sends a LE_Create_BIG_Complete event with fewer
bis_handle entries than there are BT_BOUND connections for that BIG,
or with num_bis=0, the loop reads beyond the valid bis_handle[] flex
array into adjacent heap memory.  Since the out-of-bounds values
typically exceed HCI_CONN_HANDLE_MAX (0x0EFF), hci_conn_set_handle()
rejects them and the connection remains in BT_BOUND state.  The same
connection is then found again by hci_conn_hash_lookup_big_state(),
creating an infinite loop with hci_dev_lock held.

Fix this by terminating the BIG if in case not all BIS could be setup
properly.

## References
- https://git.kernel.org/stable/c/22559ad7654f61727fc270ee4893da9f4b70cf17
- https://git.kernel.org/stable/c/5ddb8014261137cadaf83ab5617a588d80a22586
- https://git.kernel.org/stable/c/665da0baaf0396f9ed3c86ccb3955dcd0b73e774
- https://git.kernel.org/stable/c/6cb7f67bc28da787499291a562d49a084d9c90cd
- https://git.kernel.org/stable/c/77981a507aa0fc001dc37f0dd6631dd2042fed17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
