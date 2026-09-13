# [H] Bluetooth: hci_sync: Fix queuing commands when HCI_UNREGISTER is set

## Summary
Severity: High
Advisory: CVE-2022-49136
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49136
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: Fix queuing commands when HCI_UNREGISTER is set

hci_cmd_sync_queue shall return an error if HCI_UNREGISTER flag has
been set as that means hci_unregister_dev has been called so it will
likely cause a uaf after the timeout as the hdev will be freed.

## References
- https://git.kernel.org/stable/c/0b94f2651f56b9e4aa5f012b0d7eb57308c773cf
- https://git.kernel.org/stable/c/1c69ef84a808676cceb69210addf5df45b741323
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49136.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
