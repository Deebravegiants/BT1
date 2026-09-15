# [H] Bluetooth: hci_uart: clear HCI_UART_SENDING when write_work is canceled

## Summary
Severity: High
Advisory: CVE-2026-68085
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68085
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_uart: clear HCI_UART_SENDING when write_work is canceled

HCI_UART_SENDING bit in tx_state means write_work is pending and blocks
queueing it again.  Currently this bit is not cleared when canceling the
work in hci_uart_close(), which blocks future writes when device is
reopened later if write_work was pending.

Fix by clearing HCI_UART_SENDING when canceling the work.

Also make clearing of tx_skb safe by using disable_work_sync +
enable_work instead of just cancel_work_sync.  hci_uart_flush() purges
the proto tx queue so we can cancel the pending write_work there,
instead of doing it just in hci_uart_close().  Re-enable and possibly
requeue the work after queue flush.

## References
- https://git.kernel.org/stable/c/1b0d946d6f08bd39211385bc703a440911b41e46
- https://git.kernel.org/stable/c/714d861d35d937f23375a4517569b13917bbbe51
- https://git.kernel.org/stable/c/b9dd39cf1667e378b25a082ca796d495d578c5d3
- https://git.kernel.org/stable/c/d52446b3e735cfdbdc2a58342163803bc2e64249
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68085.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
