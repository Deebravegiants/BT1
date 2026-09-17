# [H] Bluetooth: avoid hci_dev_test_and_set_flag() in mgmt_init_hdev()

## Summary
Severity: High
Advisory: CVE-2022-50339
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50339
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: avoid hci_dev_test_and_set_flag() in mgmt_init_hdev()

syzbot is again reporting attempt to cancel uninitialized work
at mgmt_index_removed() [1], for setting of HCI_MGMT flag from
mgmt_init_hdev() from hci_mgmt_cmd() from hci_sock_sendmsg() can
race with testing of HCI_MGMT flag from mgmt_index_removed() from
hci_sock_bind() due to lack of serialization via hci_dev_lock().

Since mgmt_init_hdev() is called with mgmt_chan_list_lock held, we can
safely split hci_dev_test_and_set_flag() into hci_dev_test_flag() and
hci_dev_set_flag(). Thus, in order to close this race, set HCI_MGMT flag
after INIT_DELAYED_WORK() completed.

This is a local fix based on mgmt_chan_list_lock. Lack of serialization
via hci_dev_lock() might be causing different race conditions somewhere
else. But a global fix based on hci_dev_lock() should deserve a future
patch.

## References
- https://git.kernel.org/stable/c/e53c6180db8dd09de94e0a3bdf4fef6f5f9dd6e6
- https://git.kernel.org/stable/c/f74ca25d6d6629ffd4fd80a1a73037253b57d06b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50339.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50339
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
