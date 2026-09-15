# [H] Bluetooth: hci_sync: Set HCI_CMD_DRAIN_WORKQUEUE during device close

## Summary
Severity: High
Advisory: CVE-2026-63974
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63974
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: Set HCI_CMD_DRAIN_WORKQUEUE during device close

Since hci_dev_close_sync() can now be called during the reset path, we
should also set HCI_CMD_DRAIN_WORKQUEUE. This avoids queuing timeouts
while the hdev workqueue is being drained.

## References
- https://git.kernel.org/stable/c/47330cc875b36a1cf7b3543cb2cf90a7c603ce0e
- https://git.kernel.org/stable/c/525daaea459fc215f432de1b8debbd9144bf97b0
- https://git.kernel.org/stable/c/60bceb9a4c693e68cc90ba4b2dfb9e000e8638ff
- https://git.kernel.org/stable/c/9cebe4680bb9a72f80c6541eb24af06db7a1fbc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63974.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
