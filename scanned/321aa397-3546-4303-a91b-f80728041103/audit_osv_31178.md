# [H] Bluetooth: hci_core: Disable works on hci_unregister_dev

## Summary
Severity: High
Advisory: CVE-2024-58241
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2024-58241
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_core: Disable works on hci_unregister_dev

This make use of disable_work_* on hci_unregister_dev since the hci_dev is
about to be freed new submissions are not disarable.

## References
- https://git.kernel.org/stable/c/989fa5171f005ecf63440057218d8aeb1795287d
- https://git.kernel.org/stable/c/cfdb13a54e05eb98d9940cb6d1a13e7f994d811f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58241.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
