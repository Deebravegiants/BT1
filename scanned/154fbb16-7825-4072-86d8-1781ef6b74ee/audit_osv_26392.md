# [M] Bluetooth: hci_conn: Fix memory leaks

## Summary
Severity: Medium
Advisory: CVE-2023-53018
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53018
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: Fix memory leaks

When hci_cmd_sync_queue() failed in hci_le_terminate_big() or
hci_le_big_terminate(), the memory pointed by variable d is not freed,
which will cause memory leak. Add release process to error path.

## References
- https://git.kernel.org/stable/c/3aa21311f36d8a2730c7ccef37235e951f23927b
- https://git.kernel.org/stable/c/f51a825b9f730a782aa768454906b4468e67b667
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53018.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
