# [M] Bluetooth: HCI: Fix potential null-ptr-deref

## Summary
Severity: Medium
Advisory: CVE-2024-36011
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-23
Source: https://osv.dev/vulnerability/CVE-2024-36011
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: HCI: Fix potential null-ptr-deref

Fix potential null-ptr-deref in hci_le_big_sync_established_evt().

## References
- https://git.kernel.org/stable/c/1f7ebb69c1d65732bcac2fda9d15421f76f01e81
- https://git.kernel.org/stable/c/9f3be61f55d4eedc20eedc56c0f04a5ce2b4a55a
- https://git.kernel.org/stable/c/d2706004a1b8b526592e823d7e52551b518a7941
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36011.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
