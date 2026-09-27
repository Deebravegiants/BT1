# [H] Bluetooth: hci_sync: Avoid use-after-free in dbg for hci_add_adv_monitor()

## Summary
Severity: High
Advisory: CVE-2023-53828
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53828
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: Avoid use-after-free in dbg for hci_add_adv_monitor()

KSAN reports use-after-free in hci_add_adv_monitor().

While adding an adv monitor,
    hci_add_adv_monitor() calls ->
    msft_add_monitor_pattern() calls ->
    msft_add_monitor_sync() calls ->
    msft_le_monitor_advertisement_cb() calls in an error case ->
    hci_free_adv_monitor() which frees the *moniter.

This is referenced by bt_dev_dbg() in hci_add_adv_monitor().

Fix the bt_dev_dbg() by using handle instead of monitor->handle.

## References
- https://git.kernel.org/stable/c/81d8e9f59df63b8358751c1ffed9f1cf5c796909
- https://git.kernel.org/stable/c/8d66f7ced51cb924bc90278d6a0a26a52877271a
- https://git.kernel.org/stable/c/a2bcd2b63271a93a695fabbfbf459c603d956d48
- https://git.kernel.org/stable/c/aafda69d4807f5edf3558c9534be9b911774e63a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53828.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
